import frappe
from frappe import _
from frappe.utils import date_diff, nowdate

from retail_shop.utils.charts import bar_chart
from retail_shop.utils.reporting import get_sales_item_rows


def execute(filters=None):
	filters = filters or {}
	sales_rows = get_sales_item_rows(filters)
	activity = {}
	for row in sales_rows:
		entry = activity.setdefault(row.item_code, {"quantity_sold": 0, "last_sale_date": None})
		entry["quantity_sold"] += row.qty or 0
		if not row.is_return and (not entry["last_sale_date"] or row.posting_date > entry["last_sale_date"]):
			entry["last_sale_date"] = row.posting_date

	stock_rows = frappe.db.sql(
		"""
		select bin.item_code as product, sum(bin.actual_qty) as current_stock
		from `tabBin` bin
		inner join `tabItem` item on item.name = bin.item_code
		where (%s is null or item.item_group = %s)
		group by bin.item_code
		having current_stock > 0
		order by current_stock desc
		""",
		[filters.get("item_group"), filters.get("item_group")],
		as_dict=True,
	)

	data = []
	for row in stock_rows:
		summary = activity.get(row.product, {})
		last_sale_date = summary.get("last_sale_date")
		data.append(
			{
				"product": row.product,
				"current_stock": row.current_stock,
				"quantity_sold": summary.get("quantity_sold", 0),
				"last_sale_date": last_sale_date,
				"days_since_last_sale": date_diff(nowdate(), last_sale_date) if last_sale_date else None,
			}
		)

	data.sort(key=lambda row: (row["quantity_sold"], row["days_since_last_sale"] or 999999))
	chart = bar_chart(data, "product", [("quantity_sold", _("Quantity Sold"))])
	return get_columns(), data, None, chart


def get_columns():
	return [
		{"label": _("Product"), "fieldname": "product", "fieldtype": "Link", "options": "Item", "width": 180},
		{"label": _("Current Stock"), "fieldname": "current_stock", "fieldtype": "Float", "width": 120},
		{"label": _("Quantity Sold"), "fieldname": "quantity_sold", "fieldtype": "Float", "width": 120},
		{"label": _("Last Sale Date"), "fieldname": "last_sale_date", "fieldtype": "Date", "width": 120},
		{"label": _("Days Since Last Sale"), "fieldname": "days_since_last_sale", "fieldtype": "Int", "width": 150}
	]

