from uuid import uuid4

import frappe
from erpnext.accounts.party import get_party_account
from erpnext.controllers.sales_and_purchase_return import make_return_doc
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt, nowdate

from retail_shop.setup.install import ensure_retail_shop_setup
from retail_shop.setup.workspace import WORKSPACE_NAME


class TestRetailShop(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		ensure_retail_shop_setup()
		cls.company = frappe.db.get_single_value("Retail Shop Settings", "default_company")
		cls.warehouse = frappe.db.get_single_value("Retail Shop Settings", "default_warehouse")
		cls.cost_center = frappe.db.get_value("Company", cls.company, "cost_center")
		cls.currency = frappe.db.get_single_value("Retail Shop Settings", "default_currency")
		cls.income_account = frappe.db.get_value(
			"Account", {"company": cls.company, "root_type": "Income", "is_group": 0}, "name"
		)
		cls.expense_account = frappe.db.get_value(
			"Account",
			{"company": cls.company, "account_type": "Cost of Goods Sold", "is_group": 0},
			"name",
		) or frappe.db.get_value(
			"Account", {"company": cls.company, "root_type": "Expense", "is_group": 0}, "name"
		)
		cls.customer_group = frappe.db.get_value("Customer Group", {"is_group": 0}, "name")
		cls.territory = frappe.db.get_value("Territory", {"is_group": 0}, "name")
		cls.supplier_group = frappe.db.get_value("Supplier Group", {"is_group": 0}, "name")

	def setUp(self):
		self._set_commission("Percentage", percentage=2)

	def test_electrician_creation(self):
		electrician = self._make_electrician()
		self.assertTrue(electrician.electrician_name.startswith("Electrician"))
		self.assertEqual(electrician.active, 1)

	def test_workspace_is_available(self):
		workspace = frappe.get_doc("Workspace", WORKSPACE_NAME)
		self.assertEqual(workspace.module, "Retail Shop")
		self.assertEqual(workspace.public, 1)

	def test_three_shop_roles_exist(self):
		from retail_shop.setup.defaults import SALESPERSON_ROLE, SHOP_ADMIN_ROLE, TECHNICAL_ADMIN_ROLE

		for role in (TECHNICAL_ADMIN_ROLE, SHOP_ADMIN_ROLE, SALESPERSON_ROLE):
			self.assertTrue(frappe.db.exists("Role", role), role)
		self.assertFalse(frappe.db.exists("Role", "Retail Administrator"))
		self.assertFalse(frappe.db.exists("Role", "Retail Salesperson"))

	def test_shop_admin_cannot_create_users(self):
		user = self._make_user("shop-admin-users@test.local", ["Shop Admin"])
		self.assertFalse(frappe.has_permission("User", "create", user=user.name))

	def test_salesperson_cannot_create_users(self):
		user = self._make_user("salesperson-users@test.local", ["Salesperson"])
		self.assertFalse(frappe.has_permission("User", "create", user=user.name))

	def test_technical_admin_sidebar_is_filtered(self):
		from retail_shop.api.workspace import get_workspace_sidebar_items
		from retail_shop.setup.workspace import (
			SETTINGS_WORKSPACE_NAME,
			STAFF_WORKSPACE_NAME,
			WORKSPACE_NAME,
		)

		names = {page.get("name") for page in get_workspace_sidebar_items().get("pages", [])}
		self.assertEqual(names, {WORKSPACE_NAME, STAFF_WORKSPACE_NAME, SETTINGS_WORKSPACE_NAME})
		self.assertFalse(get_workspace_sidebar_items().get("has_access"))
		self.assertNotIn("Accounting", names)
		self.assertNotIn("Users", names)

	def test_shop_users_page_is_on_staff_workspace(self):
		from retail_shop.setup.workspace import STAFF_WORKSPACE_NAME

		workspace = frappe.get_doc("Workspace", STAFF_WORKSPACE_NAME)
		labels = {row.label for row in workspace.links}
		self.assertIn("Users", labels)
		self.assertNotIn("User", labels)
		self.assertTrue(any(row.link_to == "shop-users" for row in workspace.links if row.type == "Link"))

	def test_create_shop_user_with_username_and_role(self):
		from retail_shop.api.shop_users import create_shop_user, list_shop_users
		from retail_shop.setup.defaults import SALESPERSON_ROLE, SHOP_ADMIN_ROLE, TECHNICAL_ADMIN_ROLE

		username = f"cashier{uuid4().hex[:8]}"
		result = create_shop_user(username, "secret12", SALESPERSON_ROLE)
		self.assertEqual(result["username"], username)

		user = frappe.get_doc("User", result["name"])
		self.assertEqual(user.username, username)
		self.assertTrue(user.email.endswith("@kbmlight.local"))
		self.assertIn(SALESPERSON_ROLE, [row.role for row in user.roles])
		self.assertEqual(user.send_welcome_email, 0)

		named = create_shop_user(
			f"named{uuid4().hex[:6]}",
			"secret12",
			SALESPERSON_ROLE,
			email=f"named-{uuid4().hex[:6]}@example.com",
		)
		named_user = frappe.get_doc("User", named["name"])
		self.assertEqual(named_user.send_welcome_email, 0)
		self.assertFalse(named_user.email.endswith("@kbmlight.local"))

		data = list_shop_users()
		self.assertEqual(data["roles"], [TECHNICAL_ADMIN_ROLE, SHOP_ADMIN_ROLE, SALESPERSON_ROLE])
		self.assertTrue(any(row["username"] == username for row in data["users"]))

	def test_staff_password_is_required(self):
		from retail_shop.api.shop_users import create_shop_user
		from retail_shop.setup.defaults import SALESPERSON_ROLE

		with self.assertRaises(frappe.ValidationError):
			create_shop_user(f"nopassword{uuid4().hex[:6]}", "", SALESPERSON_ROLE)

	def test_shop_admin_can_only_create_salesperson(self):
		from retail_shop.api.shop_users import create_shop_user
		from retail_shop.setup.defaults import SALESPERSON_ROLE, SHOP_ADMIN_ROLE, TECHNICAL_ADMIN_ROLE

		admin = self._make_user("shop-admin-create@test.local", [SHOP_ADMIN_ROLE])
		frappe.set_user(admin.name)
		try:
			with self.assertRaises(frappe.PermissionError):
				create_shop_user(f"ta{uuid4().hex[:6]}", "secret12", TECHNICAL_ADMIN_ROLE)
			result = create_shop_user(f"sp{uuid4().hex[:6]}", "secret12", SALESPERSON_ROLE)
			self.assertEqual(result["role"], SALESPERSON_ROLE)
		finally:
			frappe.set_user("Administrator")

	def test_salesperson_cannot_manage_shop_users(self):
		from retail_shop.api.shop_users import list_shop_users

		user = self._make_user("salesperson-manage@test.local", ["Salesperson"])
		frappe.set_user(user.name)
		try:
			with self.assertRaises(frappe.PermissionError):
				list_shop_users()
		finally:
			frappe.set_user("Administrator")

	def test_purchase_entry_increases_stock(self):
		item_code = self._make_item()
		supplier = self._make_supplier()
		before_qty = self._get_stock_qty(item_code)
		entry = self._make_purchase_entry(item_code, supplier, qty=10, rate=80)
		self.assertTrue(entry.purchase_receipt)
		self.assertEqual(self._get_stock_qty(item_code), before_qty + 10)

	def test_duplicate_product_code_restocks_and_reprices(self):
		item_code = self._make_item()
		original_item_name = frappe.db.get_value("Item", item_code, "item_name")
		supplier = self._make_supplier()
		before_qty = self._get_stock_qty(item_code)

		self._make_purchase_entry(item_code, supplier, qty=10, rate=80)

		second_entry = frappe.get_doc(
			{
				"doctype": "Purchase Entry",
				"supplier": supplier,
				"posting_date": nowdate(),
				"company": self.company,
				"warehouse": self.warehouse,
				"items": [
					{
						"item_code": item_code,
						"item_name": "Should Not Overwrite Description",
						"qty": 5,
						"unit_purchase_price": 95,
						"selling_unit_price": 120,
						"minimum_selling_price": 100,
					}
				],
			}
		)
		second_entry.insert(ignore_permissions=True)
		second_entry.submit()

		# Same Product Code must restock the existing Item, never create a second one.
		self.assertEqual(frappe.db.count("Item", {"item_code": item_code}), 1)
		self.assertEqual(self._get_stock_qty(item_code), before_qty + 15)

		item = frappe.get_doc("Item", item_code)
		self.assertEqual(item.item_name, original_item_name)
		self.assertAlmostEqual(flt(item.standard_rate), 120.0, places=2)
		self.assertAlmostEqual(flt(item.last_purchase_rate), 95.0, places=2)
		self.assertAlmostEqual(flt(item.custom_purchase_unit_price), 95.0, places=2)
		self.assertAlmostEqual(flt(item.custom_minimum_selling_price), 100.0, places=2)

	def test_stock_in_fills_company_and_warehouse(self):
		item_code = self._make_item()
		supplier = self._make_supplier()
		entry = frappe.get_doc(
			{
				"doctype": "Purchase Entry",
				"supplier": supplier,
				"items": [
					{
						"item_code": item_code,
						"qty": 3,
						"unit_purchase_price": 50,
						"selling_unit_price": 80,
						"minimum_selling_price": 70,
					}
				],
			}
		)
		entry.insert(ignore_permissions=True)
		entry.submit()
		self.assertEqual(entry.company, self.company)
		self.assertEqual(entry.warehouse, self.warehouse)
		self.assertTrue(entry.purchase_receipt)

	def test_workspace_uses_shop_language_links(self):
		workspace = frappe.get_doc("Workspace", WORKSPACE_NAME)
		labels = {row.label for row in workspace.links}
		self.assertIn("Stock In", labels)
		self.assertIn("Stock Count", labels)
		self.assertIn("Products", labels)
		self.assertIn("Categories", labels)
		self.assertIn("New Sale", labels)
		self.assertIn("Sales History", labels)
		self.assertIn("Credit Sales", labels)
		self.assertNotIn("Point of Sale", labels)
		self.assertNotIn("Counter Sales", labels)
		self.assertNotIn("Sales Invoice", labels)
		self.assertNotIn("Purchase Receipt", labels)
		self.assertNotIn("Warehouse", labels)
		self.assertNotIn("Item", labels)

	def test_percentage_commission_snapshot_and_settings_change(self):
		item_code = self._make_item()
		supplier = self._make_supplier()
		self._make_purchase_entry(item_code, supplier, qty=20, rate=80)
		electrician = self._make_electrician()
		customer = self._make_customer()
		invoice = self._make_sales_invoice(item_code, customer, electrician.name, qty=2, rate=500)
		self.assertEqual(invoice.custom_commission_type, "Percentage")
		self.assertAlmostEqual(invoice.custom_commission_amount, 20.0, places=2)

		self._set_commission("Fixed Amount", fixed_amount=15)
		invoice.reload()
		self.assertAlmostEqual(invoice.custom_commission_amount, 20.0, places=2)

	def test_sale_without_electrician_allowed_by_default(self):
		item_code = self._make_item()
		supplier = self._make_supplier()
		self._make_purchase_entry(item_code, supplier, qty=10, rate=80)
		customer = self._make_customer()
		invoice = self._make_sales_invoice(item_code, customer, None, qty=1, rate=200)
		self.assertFalse(invoice.custom_commission_type)
		self.assertEqual(invoice.custom_commission_amount, 0)

	def test_require_electrician_toggle_rejects_when_enabled(self):
		settings = frappe.get_single("Retail Shop Settings")
		settings.require_electrician = 1
		settings.flags.ignore_permissions = True
		settings.save()
		self.addCleanup(self._reset_require_electrician)

		item_code = self._make_item()
		supplier = self._make_supplier()
		self._make_purchase_entry(item_code, supplier, qty=10, rate=80)
		customer = self._make_customer()
		with self.assertRaises(frappe.ValidationError):
			self._make_sales_invoice(item_code, customer, None, qty=1, rate=200)

	def test_electrician_commission_override_takes_precedence(self):
		item_code = self._make_item()
		supplier = self._make_supplier()
		self._make_purchase_entry(item_code, supplier, qty=20, rate=80)
		electrician = self._make_electrician()
		electrician.commission_type = "Fixed Amount"
		electrician.fixed_commission_amount = 50
		electrician.flags.ignore_permissions = True
		electrician.save()

		customer = self._make_customer()
		invoice = self._make_sales_invoice(item_code, customer, electrician.name, qty=2, rate=500)
		self.assertEqual(invoice.custom_commission_type, "Fixed Amount")
		self.assertAlmostEqual(invoice.custom_commission_amount, 50.0, places=2)

	def test_purchase_entry_payment_status_transitions(self):
		item_code = self._make_item()
		supplier = self._make_supplier()
		doc = frappe.get_doc(
			{
				"doctype": "Purchase Entry",
				"supplier": supplier,
				"posting_date": nowdate(),
				"company": self.company,
				"warehouse": self.warehouse,
				"items": [
					{
						"item_code": item_code,
						"qty": 10,
						"unit_purchase_price": 80,
						"selling_unit_price": 80,
						"minimum_selling_price": 75,
					},
				],
			}
		)
		doc.insert(ignore_permissions=True)
		self.assertEqual(doc.payment_status, "Unpaid")
		self.assertEqual(doc.outstanding_amount, 800)

		doc.paid_amount = 300
		doc.save(ignore_permissions=True)
		self.assertEqual(doc.payment_status, "Partial")
		self.assertEqual(doc.outstanding_amount, 500)

		doc.paid_amount = 800
		doc.save(ignore_permissions=True)
		self.assertEqual(doc.payment_status, "Paid")
		self.assertEqual(doc.outstanding_amount, 0)
		doc.submit()

	def test_salesperson_cannot_cancel_sales_invoice(self):
		user = self._make_user("retail-salesperson-cancel@test.local", ["Salesperson"])
		self.assertFalse(frappe.has_permission("Sales Invoice", "cancel", user=user.name))
		self.assertFalse(frappe.has_permission("Sales Invoice", "amend", user=user.name))
		self.assertTrue(frappe.has_permission("Sales Invoice", "submit", user=user.name))

	def test_pos_profile_allows_price_change_but_only_transaction_discount(self):
		from retail_shop.setup.defaults import POS_PROFILE_NAME

		profile = frappe.get_doc("POS Profile", POS_PROFILE_NAME)
		self.assertEqual(profile.allow_rate_change, 1)
		self.assertEqual(profile.allow_discount_change, 0)
		self.assertEqual(profile.apply_discount_on, "Net Total")
		self.assertEqual(profile.ignore_pricing_rule, 1)

		fields = {row.fieldname: row for row in frappe.get_single("POS Settings").invoice_fields}
		self.assertIn("discount_amount", fields)
		self.assertEqual(fields["discount_amount"].label, "Transaction Discount")
		self.assertEqual(fields["discount_amount"].fieldtype, "Currency")

	def test_salesperson_can_adjust_price_above_minimum(self):
		item_code = self._make_item()
		self._make_purchase_entry(item_code, self._make_supplier(), qty=5, rate=120, minimum_price=100)
		invoice = self._make_sales_invoice(
			item_code,
			self._make_customer(),
			None,
			qty=1,
			rate=110,
			price_list_rate=120,
			line_discount_percentage=8.333,
		)
		self.assertAlmostEqual(invoice.items[0].rate, 110.0, places=2)
		self.assertAlmostEqual(invoice.items[0].net_rate, 110.0, places=2)
		self.assertEqual(invoice.items[0].discount_percentage, 0)

	def test_sale_below_minimum_selling_price_is_rejected(self):
		item_code = self._make_item()
		self._make_purchase_entry(item_code, self._make_supplier(), qty=5, rate=120, minimum_price=100)
		with self.assertRaises(frappe.ValidationError):
			self._make_sales_invoice(item_code, self._make_customer(), None, qty=1, rate=99)

	def test_fixed_transaction_discount_is_applied_to_total(self):
		item_code = self._make_item()
		self._make_purchase_entry(item_code, self._make_supplier(), qty=5, rate=120, minimum_price=100)
		invoice = self._make_sales_invoice(
			item_code,
			self._make_customer(),
			None,
			qty=2,
			rate=120,
			discount_amount=20,
		)
		self.assertEqual(invoice.apply_discount_on, "Net Total")
		self.assertEqual(invoice.additional_discount_percentage, 0)
		self.assertAlmostEqual(invoice.discount_amount, 20.0, places=2)
		self.assertAlmostEqual(invoice.net_total, 220.0, places=2)
		self.assertAlmostEqual(invoice.items[0].net_rate, 110.0, places=2)

	def test_transaction_discount_cannot_push_item_below_minimum(self):
		item_code = self._make_item()
		self._make_purchase_entry(item_code, self._make_supplier(), qty=5, rate=120, minimum_price=100)
		with self.assertRaises(frappe.ValidationError):
			self._make_sales_invoice(
				item_code,
				self._make_customer(),
				None,
				qty=2,
				rate=120,
				discount_amount=50,
			)

	def test_percentage_transaction_discount_is_rejected(self):
		item_code = self._make_item()
		self._make_purchase_entry(item_code, self._make_supplier(), qty=5, rate=120, minimum_price=100)
		with self.assertRaises(frappe.ValidationError):
			self._make_sales_invoice(
				item_code,
				self._make_customer(),
				None,
				qty=1,
				rate=120,
				additional_discount_percentage=5,
			)

	def test_commission_payment_reduces_outstanding(self):
		from retail_shop.utils.commission import (
			get_commission_earned,
			get_commission_outstanding,
			get_commission_paid,
		)

		item_code = self._make_item()
		supplier = self._make_supplier()
		self._make_purchase_entry(item_code, supplier, qty=20, rate=80)
		electrician = self._make_electrician()
		customer = self._make_customer()
		self._make_sales_invoice(item_code, customer, electrician.name, qty=2, rate=500)

		self.assertAlmostEqual(get_commission_earned(electrician.name), 20.0, places=2)

		payment = frappe.get_doc(
			{
				"doctype": "Commission Payment",
				"electrician": electrician.name,
				"from_date": nowdate(),
				"to_date": nowdate(),
				"amount_paid": 15,
			}
		)
		payment.insert(ignore_permissions=True)
		payment.submit()

		self.assertAlmostEqual(get_commission_paid(electrician.name), 15.0, places=2)
		self.assertAlmostEqual(get_commission_outstanding(electrician.name), 5.0, places=2)

	def test_customer_balance_reflects_outstanding_invoice(self):
		from retail_shop.utils.balances import get_customer_balances

		item_code = self._make_item()
		supplier = self._make_supplier()
		self._make_purchase_entry(item_code, supplier, qty=5, rate=80)
		customer = self._make_customer()
		invoice = self._make_sales_invoice(item_code, customer, None, qty=1, rate=300)

		balances = {row.customer: row.balance_due for row in get_customer_balances()}
		self.assertAlmostEqual(balances.get(customer, 0), flt(invoice.outstanding_amount), places=2)

	def test_supplier_balance_reflects_unpaid_purchase(self):
		from retail_shop.utils.balances import get_supplier_balances

		item_code = self._make_item()
		supplier = self._make_supplier()
		self._make_purchase_entry(item_code, supplier, qty=10, rate=80)

		balances = {row["supplier"]: row["balance_due"] for row in get_supplier_balances()}
		self.assertAlmostEqual(balances.get(supplier, 0), 800.0, places=2)

	def test_audit_log_written_on_sale_cancel(self):
		item_code = self._make_item()
		supplier = self._make_supplier()
		self._make_purchase_entry(item_code, supplier, qty=5, rate=80)
		electrician = self._make_electrician()
		customer = self._make_customer()
		invoice = self._make_sales_invoice(item_code, customer, electrician.name, qty=1, rate=300)

		before_count = frappe.db.count(
			"Retail Audit Log", {"event_type": "Sale Cancelled", "reference_name": invoice.name}
		)
		invoice.cancel()
		after_count = frappe.db.count(
			"Retail Audit Log", {"event_type": "Sale Cancelled", "reference_name": invoice.name}
		)
		self.assertEqual(after_count, before_count + 1)

	def test_stock_reconciliation_requires_reason(self):
		item_code = self._make_item()
		self._make_purchase_entry(item_code, self._make_supplier(), qty=5, rate=80)
		doc = frappe.get_doc(
			{
				"doctype": "Stock Reconciliation",
				"purpose": "Stock Reconciliation",
				"company": self.company,
				"items": [
					{"item_code": item_code, "warehouse": self.warehouse, "qty": 8, "valuation_rate": 80}
				],
			}
		)
		with self.assertRaises(frappe.ValidationError):
			doc.insert(ignore_permissions=True)

		doc.custom_adjustment_reason = "Physical count correction"
		doc.insert(ignore_permissions=True)
		doc.submit()

		self.assertTrue(
			frappe.db.exists(
				"Retail Audit Log", {"event_type": "Inventory Adjustment", "reference_name": doc.name}
			)
		)

	def _reset_require_electrician(self):
		settings = frappe.get_single("Retail Shop Settings")
		settings.require_electrician = 0
		settings.flags.ignore_permissions = True
		settings.save()

	def test_return_reverses_commission(self):
		item_code = self._make_item()
		supplier = self._make_supplier()
		self._make_purchase_entry(item_code, supplier, qty=20, rate=80)
		electrician = self._make_electrician()
		customer = self._make_customer()
		invoice = self._make_sales_invoice(item_code, customer, electrician.name, qty=5, rate=150)
		return_doc = make_return_doc("Sales Invoice", invoice.name)
		return_doc.items[0].qty = -2
		return_doc.items[0].stock_qty = -2
		return_doc.insert()
		return_doc.submit()

		self.assertAlmostEqual(invoice.custom_commission_amount, 15.0, places=2)
		self.assertAlmostEqual(return_doc.custom_commission_amount, -6.0, places=2)

	def test_salesperson_cannot_change_commission_settings(self):
		user = self._make_user("retail-salesperson@test.local", ["Salesperson"])
		settings = frappe.get_single("Retail Commission Settings")
		with self.set_user(user.name):
			settings.reload()
			settings.commission_percentage = 5
			self.assertFalse(frappe.has_permission("Retail Commission Settings", "write", user=user.name))

	def test_salesperson_cannot_create_stock_reconciliation(self):
		user = self._make_user("retail-inventory@test.local", ["Salesperson"])
		self.assertFalse(frappe.has_permission("Stock Reconciliation", "create", user=user.name))

	def _set_commission(self, commission_type, percentage=0, fixed_amount=0):
		settings = frappe.get_single("Retail Commission Settings")
		settings.commission_type = commission_type
		settings.commission_percentage = percentage
		settings.fixed_commission_amount = fixed_amount
		settings.flags.ignore_permissions = True
		settings.save()

	def _make_item(self):
		item_code = f"RS-ITEM-{uuid4().hex[:8].upper()}"
		item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": item_code,
				"item_name": item_code,
				"stock_uom": "Nos",
				"is_stock_item": 1,
				"item_group": frappe.db.get_value("Item Group", {"is_group": 0}, "name"),
				"custom_minimum_selling_price": 1,
			}
		)
		item.insert(ignore_permissions=True)
		return item.name

	def _make_supplier(self):
		name = f"Retail Supplier {uuid4().hex[:8]}"
		supplier = frappe.get_doc(
			{
				"doctype": "Supplier",
				"supplier_name": name,
				"supplier_group": self.supplier_group,
			}
		)
		supplier.insert(ignore_permissions=True)
		return supplier.name

	def _make_customer(self):
		name = f"Retail Customer {uuid4().hex[:8]}"
		customer = frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": name,
				"customer_group": self.customer_group,
				"territory": self.territory,
				"customer_type": "Individual",
			}
		)
		customer.insert(ignore_permissions=True)
		return customer.name

	def _make_electrician(self):
		doc = frappe.get_doc(
			{
				"doctype": "Electrician",
				"electrician_name": f"Electrician {uuid4().hex[:8]}",
				"mobile_number": "0911000000",
			}
		)
		doc.insert(ignore_permissions=True)
		return doc

	def _make_purchase_entry(self, item_code, supplier, qty, rate, minimum_price=None):
		doc = frappe.get_doc(
			{
				"doctype": "Purchase Entry",
				"supplier": supplier,
				"posting_date": nowdate(),
				"company": self.company,
				"warehouse": self.warehouse,
				"items": [
					{
						"item_code": item_code,
						"qty": qty,
						"unit_purchase_price": rate,
						"selling_unit_price": rate,
						"minimum_selling_price": minimum_price if minimum_price is not None else rate,
					}
				],
			}
		)
		doc.insert(ignore_permissions=True)
		doc.submit()
		return doc

	def _make_sales_invoice(
		self,
		item_code,
		customer,
		electrician,
		qty,
		rate,
		discount_amount=0,
		additional_discount_percentage=0,
		price_list_rate=None,
		line_discount_percentage=0,
	):
		debit_to = get_party_account("Customer", customer, self.company)
		doc = frappe.get_doc(
			{
				"doctype": "Sales Invoice",
				"company": self.company,
				"posting_date": nowdate(),
				"due_date": nowdate(),
				"customer": customer,
				"debit_to": debit_to,
				"currency": self.currency,
				"conversion_rate": 1,
				"apply_discount_on": "Net Total",
				"discount_amount": discount_amount,
				"additional_discount_percentage": additional_discount_percentage,
				"update_stock": 1,
				"custom_electrician": electrician,
				"set_warehouse": self.warehouse,
				"items": [
					{
						"item_code": item_code,
						"warehouse": self.warehouse,
						"qty": qty,
						"rate": rate,
						"price_list_rate": price_list_rate if price_list_rate is not None else rate,
						"discount_percentage": line_discount_percentage,
						"income_account": self.income_account,
						"expense_account": self.expense_account,
						"cost_center": self.cost_center,
					}
				],
			}
		)
		doc.insert(ignore_permissions=True)
		doc.submit()
		return doc

	def _make_user(self, email, roles):
		if frappe.db.exists("User", email):
			user = frappe.get_doc("User", email)
		else:
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": email,
					"first_name": "Retail",
					"last_name": "User",
					"send_welcome_email": 0,
					"roles": [{"role": role} for role in roles],
				}
			)
			user.insert(ignore_permissions=True)
		return user

	def _get_stock_qty(self, item_code):
		return (
			frappe.db.sql(
				"select sum(actual_qty) from `tabBin` where item_code = %s and warehouse = %s",
				[item_code, self.warehouse],
			)[0][0]
			or 0
		)
