from frappe import _

from retail_shop.utils.balances import get_customer_balances
from retail_shop.utils.charts import bar_chart


def execute(filters=None):
	filters = filters or {}
	data = get_customer_balances(filters.get("customer"))
	chart = bar_chart(data, "customer", [("balance_due", _("Balance Due"))])
	return get_columns(), data, None, chart


def get_columns():
	return [
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 220},
		{"label": _("Balance Due"), "fieldname": "balance_due", "fieldtype": "Currency", "width": 160},
	]
