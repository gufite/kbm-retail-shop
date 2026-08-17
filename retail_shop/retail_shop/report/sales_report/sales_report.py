from frappe import _

from retail_shop.utils.charts import date_series_line_chart
from retail_shop.utils.reporting import get_sales_documents


def execute(filters=None):
	rows = get_sales_documents(filters)
	data = [
		{
			"date": row["posting_date"],
			"sale_reference": f'{row["doctype"]}: {row["name"]}',
			"salesperson": row["salesperson"],
			"electrician": row["electrician"],
			"net_sales": row["net_sales"],
			"payment_method": row["payment_method"],
			"commission": row["commission_amount"],
			"status": row["status"],
		}
		for row in rows
	]
	chart = date_series_line_chart(rows, "posting_date", "net_sales", _("Net Sales"))
	return get_columns(), data, None, chart


def get_columns():
	return [
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 110},
		{"label": _("Sale Reference"), "fieldname": "sale_reference", "fieldtype": "Data", "width": 180},
		{"label": _("Salesperson"), "fieldname": "salesperson", "fieldtype": "Data", "width": 140},
		{"label": _("Electrician"), "fieldname": "electrician", "fieldtype": "Link", "options": "Electrician", "width": 150},
		{"label": _("Net Sales"), "fieldname": "net_sales", "fieldtype": "Currency", "width": 120},
		{"label": _("Payment Method"), "fieldname": "payment_method", "fieldtype": "Data", "width": 150},
		{"label": _("Commission"), "fieldname": "commission", "fieldtype": "Currency", "width": 120},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
	]

