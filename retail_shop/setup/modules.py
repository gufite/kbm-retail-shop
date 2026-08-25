import frappe

from retail_shop.setup.defaults import (
	SHOP_ADMIN_ROLE,
	SALESPERSON_ROLE,
	TECHNICAL_ADMIN_ROLE,
)
from retail_shop.setup.workspace import WORKSPACE_NAME

ADMIN_MODULE_PROFILE = "Retail Shop Administrator Access"
SALESPERSON_MODULE_PROFILE = "Retail Shop Salesperson Access"

# Out of scope per the SRS for everyone (single shop, no manufacturing/
# CRM/projects/assets/tax-compliance/website/etc).
#
# Selling/Buying/Stock/Accounts are ALSO blocked here even though the SRS
# needs functionality that technically lives in those modules (Sales/POS
# Invoice, Item, Customer/Supplier, Payment Entry, ...). Blocking a module
# only hides its own native workspace page from the sidebar — it does not
# remove permissions on the underlying doctypes. Every doctype/report those
# native workspaces expose that the SRS actually needs (Item, Customer,
# Supplier, Warehouse, Mode of Payment, Purchase Receipt, etc.) is already
# linked directly from the shop's own workspace (see workspace.WORKSPACE_NAME),
# so nothing is lost — this just removes the native workspaces' own bloat
# (Quotation, Sales Order, Delivery Note, Purchase Order, RFQ, Supplier
# Quotation, Loyalty Program, Coupon Code, Subscription, multi-currency/tax
# setup, etc.) that the SRS never asked for, and makes our own workspace the
# single navigation entry point instead of four overlapping ones.
#
# "Core" (Users/Roles), "Setup" (System Settings et al.) and "Automation"
# (scheduled jobs) are blocked here too. Staff accounts are created through
# the shop Users page, not Frappe's User form, so none of the three shop
# roles — including Technical Admin — need those native modules on the desk.
COMMON_BLOCKED_MODULES = (
	"Accounts",
	"Assets",
	"Automation",
	"Bulk Transaction",
	"Buying",
	"Communication",
	"Core",
	"CRM",
	"EDI",
	"ERPNext Integrations",
	"Integrations",
	"Maintenance",
	"Manufacturing",
	"Portal",
	"Projects",
	"Quality Management",
	"Regional",
	"Selling",
	"Setup",
	"Social",
	"Stock",
	"Subcontracting",
	"Support",
	"Telephony",
	"Utilities",
	"Website",
)

# "Retail Shop" (this app's own Module Def — a separate, invisible technical
# identifier from the workspace's own display name/route) is never blocked
# for either role — its workspace is the sole navigation entry point now.

PROFILES = {
	ADMIN_MODULE_PROFILE: COMMON_BLOCKED_MODULES,
	SALESPERSON_MODULE_PROFILE: COMMON_BLOCKED_MODULES,
}


def ensure_module_visibility():
	for profile_name, blocked_modules in PROFILES.items():
		_ensure_module_profile(profile_name, blocked_modules)
	_apply_to_existing_users()


def _ensure_module_profile(profile_name, blocked_modules):
	if frappe.db.exists("Module Profile", profile_name):
		profile = frappe.get_doc("Module Profile", profile_name)
		# Module Profile's own on_update hook queues a background job
		# (queue_action) outside of app installation, which locks the
		# document until a worker processes it. Skip the save entirely
		# when nothing actually changed so a routine migrate never
		# re-triggers that lock/enqueue cycle.
		if {row.module for row in profile.block_modules} == set(blocked_modules):
			return profile
	else:
		profile = frappe.get_doc({"doctype": "Module Profile", "module_profile_name": profile_name})

	profile.set("block_modules", [{"module": module} for module in blocked_modules])
	profile.flags.ignore_permissions = True
	if profile.is_new():
		profile.insert(ignore_permissions=True)
	else:
		profile.save(ignore_permissions=True)
	return profile


def _apply_to_existing_users():
	users = frappe.get_all("User", filters={"name": ["!=", "Guest"]})
	for user in users:
		doc = frappe.get_doc("User", user.name)
		if _resolve_profile_name(doc) is None:
			if not _has_retail_role(doc):
				continue
		apply_module_profile_to_user(doc)
		doc.flags.ignore_permissions = True
		doc.save(ignore_permissions=True)
		ensure_home_page_default(doc)


def apply_module_profile_to_user(doc, method=None):
	"""doc_event hook (User: validate) — keep shop-role accounts
	restricted to their appropriate module set, including users created
	after initial setup. Accounts without a shop role are left untouched."""
	if doc.name == "Guest":
		return

	profile_name = _resolve_profile_name(doc)
	if not profile_name:
		return

	if doc.module_profile != profile_name:
		doc.module_profile = profile_name

	profile = frappe.get_cached_doc("Module Profile", profile_name)
	doc.set("block_modules", [{"module": row.module} for row in profile.block_modules])


def ensure_home_page_default(doc, method=None):
	"""doc_event hook (User: on_update) — Frappe's generic post-login
	landing page defaults to the site-wide "Home" workspace
	(desktop:home_page). That workspace's own module ("Setup") is blocked
	for both our roles, so the frontend rejects it as "Page home not
	found" even though boot.py's own permission fallback never fires
	(module-blocking doesn't touch Workspace *document* read permission,
	only sidebar visibility). Point every retail_shop-role user's own
	default straight at our workspace instead of relying on that
	resolution at all."""
	if doc.name == "Guest":
		return

	if not _has_retail_role(doc):
		return

	from frappe.defaults import set_user_default

	set_user_default("desktop:home_page", WORKSPACE_NAME, user=doc.name)
	if doc.default_workspace != WORKSPACE_NAME:
		frappe.db.set_value("User", doc.name, "default_workspace", WORKSPACE_NAME, update_modified=False)


def _resolve_profile_name(doc):
	roles = {role.role for role in doc.roles}
	if TECHNICAL_ADMIN_ROLE in roles or "System Manager" in roles:
		return ADMIN_MODULE_PROFILE
	if SALESPERSON_ROLE in roles and SHOP_ADMIN_ROLE not in roles:
		return SALESPERSON_MODULE_PROFILE
	if SHOP_ADMIN_ROLE in roles:
		return ADMIN_MODULE_PROFILE
	return None


def _has_retail_role(doc):
	roles = {role.role for role in doc.roles}
	return bool(
		roles.intersection({TECHNICAL_ADMIN_ROLE, "System Manager", SHOP_ADMIN_ROLE, SALESPERSON_ROLE})
	)
