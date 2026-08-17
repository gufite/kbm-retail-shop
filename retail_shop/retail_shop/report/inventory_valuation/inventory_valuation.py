import frappe
from frappe import _

from retail_shop.utils.charts import bar_chart


def execute(filters=None):
	filters = frappe._dict(filters or {})
	data = frappe.db.sql(
		"""
		select
			bin.item_code as product,
			item.item_group,
			sum(bin.actual_qty) as quantity,
			avg(bin.valuation_rate) as valuation_rate,
			sum(bin.actual_qty * bin.valuation_rate) as total_inventory_value
		from `tabBin` bin
		inner join `tabItem` item on item.name = bin.item_code
		where (%s is null or item.item_group = %s)
		group by bin.item_code, item.item_group
		order by item.item_group, bin.item_code
		""",
		[filters.get("item_group"), filters.get("item_group")],
		as_dict=True,
	)
	top_by_value = sorted(data, key=lambda row: row["total_inventory_value"] or 0, reverse=True)
	chart = bar_chart(top_by_value, "product", [("total_inventory_value", _("Inventory Value"))])
	return get_columns(), data, None, chart


def get_columns():
	return [
		{"label": _("Product"), "fieldname": "product", "fieldtype": "Link", "options": "Item", "width": 180},
		{"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 150},
		{"label": _("Quantity"), "fieldname": "quantity", "fieldtype": "Float", "width": 120},
		{"label": _("Valuation Rate"), "fieldname": "valuation_rate", "fieldtype": "Currency", "width": 120},
		{"label": _("Total Inventory Value"), "fieldname": "total_inventory_value", "fieldtype": "Currency", "width": 160}
	]

