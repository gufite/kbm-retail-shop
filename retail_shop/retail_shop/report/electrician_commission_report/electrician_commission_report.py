from collections import defaultdict

from frappe import _

from retail_shop.utils.charts import bar_chart
from retail_shop.utils.commission import get_commission_paid
from retail_shop.utils.reporting import get_sales_documents


def execute(filters=None):
	filters = filters or {}
	rows = get_sales_documents(filters)
	summary = defaultdict(
		lambda: {
			"electrician": None,
			"number_of_sales": 0,
			"total_net_sales": 0,
			"gross_commission": 0,
			"returned_adjusted_commission": 0,
			"net_commission": 0,
		}
	)
	for row in rows:
		if not row["electrician"]:
			continue
		target = summary[row["electrician"]]
		target["electrician"] = row["electrician"]
		if not row["is_return"]:
			target["number_of_sales"] += 1
			target["gross_commission"] += row["commission_amount"] or 0
		else:
			target["returned_adjusted_commission"] += abs(row["commission_amount"] or 0)
		target["total_net_sales"] += row["net_sales"] or 0
		target["net_commission"] += row["commission_amount"] or 0

	for electrician, target in summary.items():
		paid = get_commission_paid(electrician, filters.get("from_date"), filters.get("to_date"))
		target["commission_paid"] = paid
		target["commission_outstanding"] = target["net_commission"] - paid

	data = sorted(summary.values(), key=lambda row: row["net_commission"], reverse=True)
	chart = bar_chart(
		data,
		"electrician",
		[
			("commission_paid", _("Commission Paid")),
			("commission_outstanding", _("Commission Outstanding")),
		],
	)
	return get_columns(), data, None, chart


def get_columns():
	return [
		{"label": _("Electrician"), "fieldname": "electrician", "fieldtype": "Link", "options": "Electrician", "width": 180},
		{"label": _("Number of Sales"), "fieldname": "number_of_sales", "fieldtype": "Int", "width": 120},
		{"label": _("Total Net Sales"), "fieldname": "total_net_sales", "fieldtype": "Currency", "width": 140},
		{"label": _("Gross Commission"), "fieldname": "gross_commission", "fieldtype": "Currency", "width": 140},
		{"label": _("Returned/Adjusted Commission"), "fieldname": "returned_adjusted_commission", "fieldtype": "Currency", "width": 180},
		{"label": _("Net Commission"), "fieldname": "net_commission", "fieldtype": "Currency", "width": 140},
		{"label": _("Commission Paid"), "fieldname": "commission_paid", "fieldtype": "Currency", "width": 140},
		{"label": _("Commission Outstanding"), "fieldname": "commission_outstanding", "fieldtype": "Currency", "width": 160}
	]

