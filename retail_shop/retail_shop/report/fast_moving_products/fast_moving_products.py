from frappe import _

from retail_shop.utils.charts import bar_chart
from retail_shop.utils.reporting import get_sales_item_rows


def execute(filters=None):
	filters = filters or {}
	rows = get_sales_item_rows(filters)
	summary = {}
	for row in rows:
		item = summary.setdefault(
			row.item_code,
			{"product": row.item_code, "quantity_sold": 0, "sales_amount": 0, "number_of_transactions": set()},
		)
		item["quantity_sold"] += row.qty or 0
		item["sales_amount"] += row.base_net_amount or 0
		item["number_of_transactions"].add(row.voucher_no)

	data = []
	for value in summary.values():
		data.append(
			{
				"product": value["product"],
				"quantity_sold": value["quantity_sold"],
				"sales_amount": value["sales_amount"],
				"number_of_transactions": len(value["number_of_transactions"]),
			}
		)

	data.sort(key=lambda row: row["quantity_sold"], reverse=True)
	limit = int(filters.get("limit") or 20)
	data = data[:limit]
	chart = bar_chart(data, "product", [("quantity_sold", _("Quantity Sold"))])
	return get_columns(), data, None, chart


def get_columns():
	return [
		{"label": _("Product"), "fieldname": "product", "fieldtype": "Link", "options": "Item", "width": 180},
		{"label": _("Quantity Sold"), "fieldname": "quantity_sold", "fieldtype": "Float", "width": 120},
		{"label": _("Sales Amount"), "fieldname": "sales_amount", "fieldtype": "Currency", "width": 130},
		{"label": _("Number of Transactions"), "fieldname": "number_of_transactions", "fieldtype": "Int", "width": 150}
	]

