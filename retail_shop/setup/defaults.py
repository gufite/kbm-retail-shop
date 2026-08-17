import frappe
from frappe import _


RETAIL_ADMIN_ROLE = "Retail Administrator"
RETAIL_SALESPERSON_ROLE = "Retail Salesperson"
DEFAULT_MOPS = ("Cash", "Bank Transfer", "Mobile Money", "Credit")


def ensure_defaults():
	ensure_roles()
	ensure_mode_of_payments()
	ensure_walk_in_customer()
	ensure_single_defaults()
	ensure_stock_settings()
	ensure_pos_profile()
	ensure_active_domain()


def ensure_active_domain():
	# ERPNext gates several Retail-specific screens (e.g. the standard
	# Point of Sale page) behind its own "Domain" feature-flag system —
	# a page with restrict_to_domain="Retail" is silently hidden from
	# every workspace shortcut list unless "Retail" is an active domain.
	# The setup wizard normally sets this during initial company setup;
	# our own setup bypasses that wizard, so set it explicitly.
	if not frappe.db.exists("Domain", "Retail"):
		return

	settings = frappe.get_single("Domain Settings")
	if any(row.domain == "Retail" for row in settings.active_domains):
		return

	settings.append("active_domains", {"domain": "Retail"})
	settings.flags.ignore_permissions = True
	settings.save(ignore_permissions=True)
	frappe.cache.delete_value("domain_restricted_pages")
	frappe.cache.delete_value("domain_restricted_doctypes")


def ensure_roles():
	for role_name in (RETAIL_ADMIN_ROLE, RETAIL_SALESPERSON_ROLE):
		if not frappe.db.exists("Role", role_name):
			frappe.get_doc({"doctype": "Role", "role_name": role_name}).insert(ignore_permissions=True)


def ensure_mode_of_payments():
	for mode_name in DEFAULT_MOPS:
		type_name = "Cash" if mode_name == "Cash" else "Bank"
		if mode_name == "Credit":
			type_name = "General"

		if frappe.db.exists("Mode of Payment", mode_name):
			doc = frappe.get_doc("Mode of Payment", mode_name)
		else:
			doc = frappe.get_doc(
				{
					"doctype": "Mode of Payment",
					"mode_of_payment": mode_name,
					"type": type_name,
					"enabled": 1,
				}
			)
			doc.insert(ignore_permissions=True)

		_ensure_mode_of_payment_account(doc, type_name)


def _ensure_mode_of_payment_account(doc, type_name):
	# Required before a Mode of Payment can be used in a POS Profile /
	# Payment Entry — without a default account, POS throws "Please set
	# default Cash or Bank account" the moment you try to open a shift.
	company = frappe.db.get_single_value("Retail Shop Settings", "default_company")
	if not company or any(row.company == company for row in doc.accounts):
		return

	account_type = "Cash" if type_name == "Cash" else "Bank"
	default_account = frappe.db.get_value(
		"Account", {"company": company, "account_type": account_type, "is_group": 0}, "name"
	)
	if not default_account:
		default_account = _create_leaf_account(company, account_type)
	if not default_account:
		return

	doc.append("accounts", {"company": company, "default_account": default_account})
	doc.flags.ignore_permissions = True
	doc.save(ignore_permissions=True)


def _create_leaf_account(company, account_type):
	# The Standard Chart of Accounts only creates a "Bank Accounts" group
	# header, not an actual postable bank account — every real setup is
	# expected to add its own. Create a minimal default one so Mode of
	# Payment / POS Profile have something usable out of the box.
	parent = frappe.db.get_value(
		"Account", {"company": company, "account_type": account_type, "is_group": 1}, "name"
	)
	if not parent:
		return None

	name = f"{account_type} Account"
	if frappe.db.exists("Account", f"{name} - {frappe.get_cached_value('Company', company, 'abbr')}"):
		return f"{name} - {frappe.get_cached_value('Company', company, 'abbr')}"

	doc = frappe.get_doc(
		{
			"doctype": "Account",
			"account_name": name,
			"company": company,
			"parent_account": parent,
			"account_type": account_type,
			"is_group": 0,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def ensure_walk_in_customer():
	customer_name = "Walk-in Customer"
	if frappe.db.exists("Customer", customer_name):
		return customer_name

	customer_group = frappe.db.get_value("Customer Group", {"is_group": 0}, "name")
	territory = frappe.db.get_value("Territory", {"is_group": 0}, "name")
	if not customer_group or not territory:
		return None

	doc = frappe.get_doc(
		{
			"doctype": "Customer",
			"customer_name": customer_name,
			"customer_group": customer_group,
			"territory": territory,
			"customer_type": "Individual",
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def ensure_single_defaults():
	settings = frappe.get_single("Retail Shop Settings")
	if not settings.default_company:
		settings.default_company = frappe.db.get_value("Company", {}, "name", order_by="creation asc")

	if settings.default_company and not settings.default_currency:
		settings.default_currency = frappe.db.get_value(
			"Company", settings.default_company, "default_currency"
		)

	if not settings.default_warehouse and settings.default_company:
		settings.default_warehouse = frappe.db.get_value(
			"Warehouse",
			{"company": settings.default_company, "is_group": 0},
			"name",
			order_by="creation asc",
		)

	if not settings.default_walk_in_customer:
		settings.default_walk_in_customer = ensure_walk_in_customer()

	if not settings.default_item_group:
		settings.default_item_group = frappe.db.get_value(
			"Item Group", {"is_group": 0}, "name", order_by="creation asc"
		)

	settings.flags.ignore_permissions = True
	settings.save()

	# System Settings.currency is a separate global default from the
	# Company's own currency and from Retail Shop Settings.default_currency
	# above — nothing keeps it in sync automatically, so a shop whose
	# currency was set/changed after initial setup (e.g. away from the
	# test-bootstrap's USD) still shows the old currency wherever the UI
	# falls back to this System Settings value instead of the Company's.
	if settings.default_currency:
		system_settings = frappe.get_single("System Settings")
		if system_settings.currency != settings.default_currency:
			system_settings.currency = settings.default_currency
			system_settings.flags.ignore_permissions = True
			system_settings.save()

	commission_settings = frappe.get_single("Retail Commission Settings")
	if not commission_settings.commission_type:
		commission_settings.commission_type = "Percentage"
		commission_settings.commission_percentage = 0
		commission_settings.flags.ignore_permissions = True
		commission_settings.save()


def ensure_stock_settings():
	stock_settings = frappe.get_single("Stock Settings")
	if stock_settings.valuation_method != "Moving Average":
		stock_settings.valuation_method = "Moving Average"
		stock_settings.flags.ignore_permissions = True
		stock_settings.save()


POS_PROFILE_NAME = "Retail Shop POS"


def ensure_pos_profile():
	# Required before anyone can open the standard Point of Sale screen —
	# without one, POS Invoice's own doctype permissions never even get
	# checked because the opening-shift dialog has nothing to select.
	settings = frappe.get_single("Retail Shop Settings")

	if frappe.db.exists("POS Profile", POS_PROFILE_NAME):
		# The POS screen reads POS Profile.customer (not Retail Shop
		# Settings.default_walk_in_customer directly) to prefill the sale's
		# customer before any item can be added — without it, the screen
		# blocks item entry on every sale, credit or not. Self-heal existing
		# profiles left over from before this field was set on creation.
		if settings.default_walk_in_customer and not frappe.db.get_value(
			"POS Profile", POS_PROFILE_NAME, "customer"
		):
			frappe.db.set_value("POS Profile", POS_PROFILE_NAME, "customer", settings.default_walk_in_customer)
		return

	company = settings.default_company
	warehouse = settings.default_warehouse
	if not company or not warehouse:
		return

	cost_center = frappe.db.get_value("Company", company, "cost_center")
	write_off_account = frappe.db.get_value(
		"Account", {"company": company, "root_type": "Expense", "is_group": 0}, "name"
	)

	doc = frappe.get_doc(
		{
			"doctype": "POS Profile",
			"name": POS_PROFILE_NAME,
			"company": company,
			"warehouse": warehouse,
			"currency": settings.default_currency,
			"customer": settings.default_walk_in_customer,
			"write_off_account": write_off_account,
			"write_off_cost_center": cost_center,
			"write_off_limit": 0,
			"payments": [
				{"mode_of_payment": mode, "default": 1 if mode == "Cash" else 0}
				for mode in DEFAULT_MOPS
				if mode != "Credit"
			],
		}
	)
	doc.insert(ignore_permissions=True)


def get_default_company():
	company = frappe.db.get_single_value("Retail Shop Settings", "default_company")
	if not company:
		frappe.throw(_("Retail Shop Settings requires a default company."))
	return company

