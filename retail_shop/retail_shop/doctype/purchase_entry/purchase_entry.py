import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate

from retail_shop.setup.defaults import get_default_company


class PurchaseEntry(Document):
	def validate(self):
		if not self.company:
			self.company = frappe.db.get_single_value("Retail Shop Settings", "default_company") or get_default_company()
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
			row.conversion_factor = self._resolve_conversion_factor(row)
			total_qty += flt(row.qty)
			total_amount += flt(row.amount)

		self.total_qty = total_qty
		self.total_amount = total_amount

		if flt(self.paid_amount) > flt(total_amount) + 0.005:
			frappe.throw(
				_("Paid Amount ({0}) cannot exceed the Purchase Entry's total amount ({1}).").format(
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
		"""Product Code upsert: an existing code restocks/repriced the same
		product; a new code creates one. See SRS Sec. 5 / Stock Input spec."""
		existing = frappe.db.get_value("Item", row.item_code, ["item_name", "stock_uom"], as_dict=True)

		if existing:
			# Duplicate product: keep the existing code & description as-is,
			# only the prices move — the description typed on this row (if
			# any) is discarded, not written back.
			row.item_name = existing.item_name
			row.uom = row.uom or existing.stock_uom
			frappe.db.set_value("Item", row.item_code, "standard_rate", flt(row.selling_unit_price))
			return

		if not row.item_name:
			frappe.throw(
				_("Row #{0}: Product Description is required to create a new product for code {1}.").format(
					row.idx, frappe.bold(row.item_code)
				)
			)

		item_group = frappe.db.get_single_value("Retail Shop Settings", "default_item_group")
		if not item_group:
			frappe.throw(_("Retail Shop Settings requires a default Item Group for new products."))

		row.uom = row.uom or frappe.db.get_single_value("Stock Settings", "stock_uom") or "Nos"
		frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": row.item_code,
				"item_name": row.item_name,
				"item_group": item_group,
				"stock_uom": row.uom,
				"is_stock_item": 1,
				"standard_rate": flt(row.selling_unit_price),
			}
		).insert(ignore_permissions=True)

	def _resolve_conversion_factor(self, row) -> float:
		stock_uom = frappe.db.get_value("Item", row.item_code, "stock_uom")
		if not row.uom or row.uom == stock_uom:
			return 1

		conversion_factor = frappe.db.get_value(
			"UOM Conversion Detail", {"parent": row.item_code, "uom": row.uom}, "conversion_factor"
		)
		if not conversion_factor:
			frappe.throw(
				_("Item {0} has no conversion factor defined for UOM {1}. Add it under the item's UOMs table.").format(
					frappe.bold(row.item_code), frappe.bold(row.uom)
				)
			)
		return flt(conversion_factor)

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
						"conversion_factor": row.conversion_factor,
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

