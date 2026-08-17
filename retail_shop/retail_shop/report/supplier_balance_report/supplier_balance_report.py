from frappe import _

from retail_shop.utils.balances import get_supplier_balances
from retail_shop.utils.charts import bar_chart


def execute(filters=None):
	filters = filters or {}
	data = get_supplier_balances(filters.get("supplier"))
	chart = bar_chart(data, "supplier", [("balance_due", _("Balance Due"))])
	return get_columns(), data, None, chart


def get_columns():
	return [
		{"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 220},
		{"label": _("Balance Due"), "fieldname": "balance_due", "fieldtype": "Currency", "width": 160},
	]
