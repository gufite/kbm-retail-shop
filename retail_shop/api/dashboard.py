from datetime import timedelta

import frappe
from frappe.utils import getdate, nowdate

from retail_shop.utils.balances import get_total_customer_balance_due, get_total_supplier_balance_owed
from retail_shop.utils.commission import get_total_commission_summary
from retail_shop.utils.inventory import get_stock_alert_counts
from retail_shop.utils.reporting import get_sales_documents


@frappe.whitelist()
def get_dashboard_data():
	frappe.only_for(("Administrator", "Retail Administrator", "Retail Salesperson"))
	today = getdate(nowdate())
	week_start = today - timedelta(days=today.weekday())
	month_start = today.replace(day=1)
	sales_rows = get_sales_documents()
	inventory_totals = frappe.db.sql(
		"""
		select
			sum(actual_qty * valuation_rate) as inventory_value,
			sum(case when actual_qty > 0 then 1 else 0 end) as products_in_stock,
			sum(case when actual_qty <= 0 then 1 else 0 end) as out_of_stock_products
		from `tabBin`
		""",
		as_dict=True,
	)[0]
	stock_alerts = get_stock_alert_counts()

	def sum_period(start_date):
		return sum(row["net_sales"] for row in sales_rows if getdate(row["posting_date"]) >= start_date)

	top_products = _get_top_products()
	top_electricians = _get_top_electricians()
	profit_summary = _get_profit_summary()

	return {
		"today_sales": sum(row["net_sales"] for row in sales_rows if getdate(row["posting_date"]) == today),
		"weekly_sales": sum_period(week_start),
		"monthly_sales": sum_period(month_start),
		"current_inventory_value": inventory_totals.inventory_value or 0,
		"total_products_in_stock": inventory_totals.products_in_stock or 0,
		"low_stock_products": stock_alerts["low_stock_count"],
		"out_of_stock_products": inventory_totals.out_of_stock_products or 0,
		"top_selling_products": top_products,
		"revenue_summary": {
			"today": sum(row["net_sales"] for row in sales_rows if getdate(row["posting_date"]) == today),
			"week": sum_period(week_start),
			"month": sum_period(month_start),
		},
		"profit_summary": profit_summary,
		"commission_summary": get_total_commission_summary(),
		"top_performing_electricians": top_electricians,
		"total_customer_balance_due": get_total_customer_balance_due(),
		"total_supplier_balance_owed": get_total_supplier_balance_owed(),
	}


def _get_top_products():
	return frappe.db.sql(
		"""
		select
			item_code,
			sum(qty) as quantity_sold,
			sum(base_net_amount) as sales_amount
		from (
			select item.item_code, item.qty, item.base_net_amount
			from `tabPOS Invoice Item` item
			inner join `tabPOS Invoice` doc on doc.name = item.parent
			where doc.docstatus = 1
			union all
			select item.item_code, item.qty, item.base_net_amount
			from `tabSales Invoice Item` item
			inner join `tabSales Invoice` doc on doc.name = item.parent
			where doc.docstatus = 1 and doc.update_stock = 1
		) sales_items
		group by item_code
		order by quantity_sold desc
		limit 5
		""",
		as_dict=True,
	)


def _get_top_electricians():
	return frappe.db.sql(
		"""
		select
			custom_electrician as electrician,
			sum(net_total) as net_sales,
			sum(custom_commission_amount) as commission
		from (
			select custom_electrician, net_total, custom_commission_amount
			from `tabPOS Invoice`
			where docstatus = 1 and custom_electrician is not null and custom_electrician != ''
			union all
			select custom_electrician, net_total, custom_commission_amount
			from `tabSales Invoice`
			where docstatus = 1 and update_stock = 1 and custom_electrician is not null and custom_electrician != ''
		) sales_docs
		group by custom_electrician
		order by commission desc
		limit 5
		""",
		as_dict=True,
	)


def _get_profit_summary():
	row = frappe.db.sql(
		"""
		select
			sum(revenue) as revenue,
			sum(cost) as cost,
			sum(revenue - cost) as gross_profit
		from (
			select
				item.base_net_amount as revenue,
				coalesce(-sle.stock_value_difference, 0) as cost
			from `tabPOS Invoice Item` item
			inner join `tabPOS Invoice` doc on doc.name = item.parent and doc.docstatus = 1
			left join `tabStock Ledger Entry` sle
				on sle.voucher_type = 'POS Invoice'
				and sle.voucher_no = doc.name
				and sle.voucher_detail_no = item.name
				and sle.is_cancelled = 0
			union all
			select
				item.base_net_amount as revenue,
				coalesce(-sle.stock_value_difference, 0) as cost
			from `tabSales Invoice Item` item
			inner join `tabSales Invoice` doc on doc.name = item.parent and doc.docstatus = 1 and doc.update_stock = 1
			left join `tabStock Ledger Entry` sle
				on sle.voucher_type = 'Sales Invoice'
				and sle.voucher_no = doc.name
				and sle.voucher_detail_no = item.name
				and sle.is_cancelled = 0
		) profit_lines
		""",
		as_dict=True,
	)[0]
	revenue = row.revenue or 0
	cost = row.cost or 0
	profit = row.gross_profit or 0
	return {
		"revenue": revenue,
		"cost": cost,
		"gross_profit": profit,
		"gross_margin_percent": (profit / revenue * 100) if revenue else 0,
	}

