import frappe
from frappe.utils import flt


def get_customer_balances(customer: str = None):
	condition = "where t.customer = %s" if customer else ""
	params = [customer] if customer else []
	return frappe.db.sql(
		f"""
		select customer, sum(outstanding_amount) as balance_due
		from (
			select customer, outstanding_amount from `tabSales Invoice` where docstatus = 1 and update_stock = 1
			union all
			select customer, outstanding_amount from `tabPOS Invoice` where docstatus = 1
		) t
		{condition}
		group by customer
		having balance_due > 0
		order by balance_due desc
		""",
		params,
		as_dict=True,
	)


def get_total_customer_balance_due() -> float:
	rows = get_customer_balances()
	return flt(sum(row.balance_due for row in rows))


def get_supplier_balances(supplier: str = None):
	filters = {"docstatus": 1}
	if supplier:
		filters["supplier"] = supplier

	rows = frappe.get_all("Purchase Entry", filters=filters, fields=["supplier", "outstanding_amount"])
	totals = {}
	for row in rows:
		totals[row.supplier] = totals.get(row.supplier, 0) + flt(row.outstanding_amount)

	balances = [{"supplier": supplier, "balance_due": balance} for supplier, balance in totals.items() if balance > 0]
	balances.sort(key=lambda row: row["balance_due"], reverse=True)
	return balances


def get_total_supplier_balance_owed() -> float:
	rows = get_supplier_balances()
	return flt(sum(row["balance_due"] for row in rows))
