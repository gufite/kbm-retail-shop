import frappe
from frappe import _

from retail_shop.utils.charts import bar_chart


def execute(filters=None):
	filters = frappe._dict(filters or {})
	params = []
	date_clause = ""
	item_clause = ""
	item_group_clause = ""
	if filters.get("from_date") and filters.get("to_date"):
		date_clause = "and doc.posting_date between %s and %s"
		params.extend([filters.from_date, filters.to_date])
	if filters.get("product"):
		item_clause = "and item.item_code = %s"
		params.append(filters.product)
	if filters.get("item_group"):
		item_group_clause = "and item.item_group = %s"
		params.append(filters.item_group)

	sales_query = f"""
		select
			item.item_code,
			item.item_group,
			sum(item.base_net_amount) as revenue,
			sum(coalesce(-sle.stock_value_difference, 0)) as cost
		from `tabPOS Invoice Item` item
		inner join `tabPOS Invoice` doc on doc.name = item.parent and doc.docstatus = 1
		left join `tabStock Ledger Entry` sle
			on sle.voucher_type = 'POS Invoice'
			and sle.voucher_no = doc.name
			and sle.voucher_detail_no = item.name
			and sle.is_cancelled = 0
		where 1 = 1 {date_clause} {item_clause} {item_group_clause}
		group by item.item_code, item.item_group
		union all
		select
			item.item_code,
			item.item_group,
			sum(item.base_net_amount) as revenue,
			sum(coalesce(-sle.stock_value_difference, 0)) as cost
		from `tabSales Invoice Item` item
		inner join `tabSales Invoice` doc on doc.name = item.parent and doc.docstatus = 1 and doc.update_stock = 1
		left join `tabStock Ledger Entry` sle
			on sle.voucher_type = 'Sales Invoice'
			and sle.voucher_no = doc.name
			and sle.voucher_detail_no = item.name
			and sle.is_cancelled = 0
		where 1 = 1 {date_clause} {item_clause} {item_group_clause}
		group by item.item_code, item.item_group
	"""
	union_params = params + params
	rows = frappe.db.sql(
		f"""
		select
			item_code as product,
			item_group,
			sum(revenue) as revenue,
			sum(cost) as cost
		from ({sales_query}) profit_lines
		group by item_code, item_group
		order by product
		""",
		union_params,
		as_dict=True,
	)
	for row in rows:
		row["gross_profit"] = (row["revenue"] or 0) - (row["cost"] or 0)
		row["gross_margin_percent"] = (row["gross_profit"] / row["revenue"] * 100) if row["revenue"] else 0

	top_by_revenue = sorted(rows, key=lambda row: row["revenue"] or 0, reverse=True)
	chart = bar_chart(
		top_by_revenue,
		"product",
		[("revenue", _("Revenue")), ("gross_profit", _("Gross Profit"))],
	)
	return get_columns(), rows, None, chart


def get_columns():
	return [
		{"label": _("Product"), "fieldname": "product", "fieldtype": "Link", "options": "Item", "width": 160},
		{"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 140},
		{"label": _("Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 120},
		{"label": _("Cost"), "fieldname": "cost", "fieldtype": "Currency", "width": 120},
		{"label": _("Gross Profit"), "fieldname": "gross_profit", "fieldtype": "Currency", "width": 120},
		{"label": _("Gross Margin %"), "fieldname": "gross_margin_percent", "fieldtype": "Percent", "width": 120}
	]

