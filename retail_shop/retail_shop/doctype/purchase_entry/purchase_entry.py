import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate

from retail_shop.setup.defaults import get_default_company
from retail_shop.utils.products import default_stock_uom, update_product_prices


class PurchaseEntry(Document):
	def validate(self):
		if not self.company:
			self.company = (
				frappe.db.get_single_value("Retail Shop Settings", "default_company") or get_default_company()
			)
		if not self.warehouse:
			self.warehouse = frappe.db.get_single_value("Retail Shop Settings", "default_warehouse")
		if not self.warehouse:
			frappe.throw(_("Retail Shop Settings requires a default warehouse for Purchase Entry."))
		if not self.posting_date:
			self.posting_date = nowdate()

		total_qty = 0
		total_amount = 0
		for row in self.items:
			self._ensure_product(row)
			row.amount = flt(row.qty) * flt(row.unit_purchase_price)
			row.conversion_factor = 1
			total_qty += flt(row.qty)
			total_amount += flt(row.amount)

		self.total_qty = total_qty
		self.total_amount = total_amount

		if flt(self.paid_amount) > flt(total_amount) + 0.005:
			frappe.throw(
				_("Paid Amount ({0}) cannot exceed the total amount ({1}).").format(
					frappe.format_value(self.paid_amount, {"fieldtype": "Currency"}),
					frappe.format_value(total_amount, {"fieldtype": "Currency"}),
				)
			)

		self.outstanding_amount = flt(total_amount) - flt(self.paid_amount)
		if flt(self.paid_amount) <= 0:
			self.payment_status = "Unpaid"
		elif self.outstanding_amount <= 0:
			self.payment_status = "Paid"
		else:
			self.payment_status = "Partial"

	def _ensure_product(self, row):
		"""Product Code upsert: an existing code restocks/reprices the same
		product; a new code creates one. See SRS Sec. 5 / Stock Input spec."""
		existing = frappe.db.get_value(
			"Item",
			row.item_code,
			["item_name", "stock_uom", "custom_minimum_selling_price"],
			as_dict=True,
		)

		if existing:
			# Duplicate product: keep the existing code & description as-is,
			# only quantity and prices move — a description typed on this row
			# (if any) is discarded, not written back.
			if row.item_name and row.item_name != existing.item_name:
				frappe.msgprint(
					_(
						"Product {0} already exists. Quantity will be added to current stock, "
						"and the description will stay as {1}."
					).format(frappe.bold(row.item_code), frappe.bold(existing.item_name)),
					alert=True,
					indicator="blue",
				)
			row.item_name = existing.item_name
			row.uom = existing.stock_uom
			if row.minimum_selling_price in (None, ""):
				row.minimum_selling_price = existing.custom_minimum_selling_price or row.selling_unit_price
			self._validate_product_prices(row)
			update_product_prices(
				row.item_code,
				row.unit_purchase_price,
				row.selling_unit_price,
				row.minimum_selling_price,
			)
			return

		if not row.item_name:
			frappe.throw(
				_("Row #{0}: Product Description is required to create a new product for code {1}.").format(
					row.idx, frappe.bold(row.item_code)
				)
			)
		self._validate_product_prices(row)

		item_group = frappe.db.get_single_value("Retail Shop Settings", "default_item_group")
		if not item_group:
			frappe.throw(_("Retail Shop Settings requires a default category for new products."))

		row.uom = default_stock_uom()
		item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": row.item_code,
				"item_name": row.item_name,
				"item_group": item_group,
				"stock_uom": row.uom,
				"is_stock_item": 1,
				"standard_rate": flt(row.selling_unit_price),
				"last_purchase_rate": flt(row.unit_purchase_price),
			}
		)
		if frappe.db.has_column("Item", "custom_purchase_unit_price"):
			item.custom_purchase_unit_price = flt(row.unit_purchase_price)
		if frappe.db.has_column("Item", "custom_minimum_selling_price"):
			item.custom_minimum_selling_price = flt(row.minimum_selling_price)
		item.insert(ignore_permissions=True)
		update_product_prices(
			row.item_code,
			row.unit_purchase_price,
			row.selling_unit_price,
			row.minimum_selling_price,
		)

	def _validate_product_prices(self, row):
		minimum_price = flt(row.minimum_selling_price)
		selling_price = flt(row.selling_unit_price)
		if minimum_price <= 0:
			frappe.throw(_("Row #{0}: Minimum Selling Price must be greater than zero.").format(row.idx))
		if selling_price < minimum_price:
			frappe.throw(
				_("Row #{0}: Selling Unit Price cannot be lower than Minimum Selling Price.").format(row.idx)
			)

	def on_submit(self):
		if self.purchase_receipt:
			return

		purchase_receipt = frappe.get_doc(
			{
				"doctype": "Purchase Receipt",
				"supplier": self.supplier,
				"company": self.company,
				"posting_date": self.posting_date,
				"set_warehouse": self.warehouse,
				"custom_purchase_entry": self.name,
				"items": [
					{
						"item_code": row.item_code,
						"qty": row.qty,
						"uom": row.uom,
						"conversion_factor": 1,
						"rate": row.unit_purchase_price,
						"warehouse": self.warehouse,
					}
					for row in self.items
				],
			}
		)
		purchase_receipt.insert(ignore_permissions=True)
		purchase_receipt.submit()
		self.db_set("purchase_receipt", purchase_receipt.name)

	def on_cancel(self):
		if not self.purchase_receipt:
			return

		purchase_receipt = frappe.get_doc("Purchase Receipt", self.purchase_receipt)
		if purchase_receipt.docstatus == 1:
			purchase_receipt.cancel()
