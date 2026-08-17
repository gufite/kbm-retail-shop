import frappe
from frappe import _

from retail_shop.utils.charts import date_series_line_chart


def execute(filters=None):
	filters = frappe._dict(filters or {})
	conditions = ["doc.docstatus = 1"]
	params = []
	if filters.get("from_date") and filters.get("to_date"):
		conditions.append("doc.posting_date between %s and %s")
		params.extend([filters.from_date, filters.to_date])
	if filters.get("supplier"):
		conditions.append("doc.supplier = %s")
		params.append(filters.supplier)
	if filters.get("product"):
		conditions.append("item.item_code = %s")
		params.append(filters.product)

	data = frappe.db.sql(
		f"""
		select
			doc.posting_date as date,
			doc.name as purchase_reference,
			doc.supplier,
			item.item_code as product,
			item.qty as quantity,
			item.rate as unit_cost,
			item.amount
		from `tabPurchase Receipt` doc
		inner join `tabPurchase Receipt Item` item on item.parent = doc.name
		where {' and '.join(conditions)}
		order by doc.posting_date desc, doc.name desc
		""",
		params,
		as_dict=True,
	)
	chart = date_series_line_chart(data, "date", "amount", _("Purchase Amount"))
	return get_columns(), data, None, chart


def get_columns():
	return [
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 110},
		{"label": _("Purchase Reference"), "fieldname": "purchase_reference", "fieldtype": "Link", "options": "Purchase Receipt", "width": 180},
		{"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 160},
		{"label": _("Product"), "fieldname": "product", "fieldtype": "Link", "options": "Item", "width": 160},
		{"label": _("Quantity"), "fieldname": "quantity", "fieldtype": "Float", "width": 100},
		{"label": _("Unit Cost"), "fieldname": "unit_cost", "fieldtype": "Currency", "width": 110},
		{"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 120}
	]

