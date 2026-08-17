from uuid import uuid4

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt, nowdate

from erpnext.accounts.party import get_party_account
from erpnext.controllers.sales_and_purchase_return import make_return_doc

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
		) or frappe.db.get_value("Account", {"company": cls.company, "root_type": "Expense", "is_group": 0}, "name")
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
					{"item_code": item_code, "qty": 10, "unit_purchase_price": 80, "selling_unit_price": 80},
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
		user = self._make_user("retail-salesperson-cancel@test.local", ["Retail Salesperson"])
		self.assertFalse(frappe.has_permission("Sales Invoice", "cancel", user=user.name))
		self.assertFalse(frappe.has_permission("Sales Invoice", "amend", user=user.name))
		self.assertTrue(frappe.has_permission("Sales Invoice", "submit", user=user.name))

	def test_commission_payment_reduces_outstanding(self):
		from retail_shop.utils.commission import get_commission_earned, get_commission_outstanding, get_commission_paid

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
				"items": [{"item_code": item_code, "warehouse": self.warehouse, "qty": 8, "valuation_rate": 80}],
			}
		)
		with self.assertRaises(frappe.ValidationError):
			doc.insert(ignore_permissions=True)

		doc.custom_adjustment_reason = "Physical count correction"
		doc.insert(ignore_permissions=True)
		doc.submit()

		self.assertTrue(
			frappe.db.exists("Retail Audit Log", {"event_type": "Inventory Adjustment", "reference_name": doc.name})
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
		user = self._make_user("retail-salesperson@test.local", ["Retail Salesperson"])
		settings = frappe.get_single("Retail Commission Settings")
		with self.set_user(user.name):
			settings.reload()
			settings.commission_percentage = 5
			self.assertFalse(frappe.has_permission("Retail Commission Settings", "write", user=user.name))

	def test_salesperson_cannot_create_stock_reconciliation(self):
		user = self._make_user("retail-inventory@test.local", ["Retail Salesperson"])
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

	def _make_purchase_entry(self, item_code, supplier, qty, rate):
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
					}
				],
			}
		)
		doc.insert(ignore_permissions=True)
		doc.submit()
		return doc

	def _make_sales_invoice(self, item_code, customer, electrician, qty, rate):
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
				"update_stock": 1,
				"custom_electrician": electrician,
				"set_warehouse": self.warehouse,
				"items": [
					{
						"item_code": item_code,
						"warehouse": self.warehouse,
						"qty": qty,
						"rate": rate,
						"price_list_rate": rate,
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
