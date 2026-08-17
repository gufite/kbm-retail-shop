from __future__ import annotations

import frappe

from retail_shop.utils.sales import get_payment_method_label


def get_sales_documents(filters=None):
	filters = frappe._dict(filters or {})
	pos_docs = frappe.get_all(
		"POS Invoice",
		filters=_get_doc_filters(filters),
		fields=[
			"name",
			"posting_date",
			"owner",
			"custom_electrician",
			"net_total",
			"base_net_total",
			"custom_commission_amount",
			"status",
			"outstanding_amount",
			"is_return",
		],
		order_by="posting_date desc, modified desc",
	)
	sales_docs = frappe.get_all(
		"Sales Invoice",
		filters={**_get_doc_filters(filters), "update_stock": 1},
		fields=[
			"name",
			"posting_date",
			"owner",
			"custom_electrician",
			"net_total",
			"base_net_total",
			"custom_commission_amount",
			"status",
			"outstanding_amount",
			"is_return",
		],
		order_by="posting_date desc, modified desc",
	)

	rows = []
	for doctype, docs in (("POS Invoice", pos_docs), ("Sales Invoice", sales_docs)):
		for row in docs:
			doc = frappe.get_cached_doc(doctype, row.name)
			rows.append(
				{
					"doctype": doctype,
					"name": row.name,
					"posting_date": row.posting_date,
					"salesperson": row.owner,
					"electrician": row.custom_electrician,
					"net_sales": row.net_total,
					"base_net_sales": row.base_net_total,
					"commission_amount": row.custom_commission_amount,
					"status": row.status,
					"payment_method": get_payment_method_label(doc),
					"is_return": row.is_return,
				}
			)

	if filters.payment_method:
		rows = [row for row in rows if filters.payment_method in (row.get("payment_method") or "")]

	if filters.salesperson:
		rows = [row for row in rows if row.get("salesperson") == filters.salesperson]

	rows.sort(key=lambda row: (row["posting_date"], row["name"]), reverse=True)
	return rows


def get_sales_item_rows(filters=None):
	filters = frappe._dict(filters or {})
	return frappe.db.sql(
		"""
		select * from (
			select
				'POS Invoice' as doctype,
				doc.name as voucher_no,
				doc.posting_date,
				doc.owner as salesperson,
				doc.custom_electrician as electrician,
				doc.is_return,
				item.item_code,
				item.item_name,
				item.item_group,
				item.warehouse,
				item.qty,
				item.stock_qty,
				item.net_amount,
				item.base_net_amount
			from `tabPOS Invoice Item` item
			inner join `tabPOS Invoice` doc on doc.name = item.parent
			where doc.docstatus = 1
				{date_clause}
				{electrician_clause}
				{item_clause}
				{item_group_clause}
			union all
			select
				'Sales Invoice' as doctype,
				doc.name as voucher_no,
				doc.posting_date,
				doc.owner as salesperson,
				doc.custom_electrician as electrician,
				doc.is_return,
				item.item_code,
				item.item_name,
				item.item_group,
				item.warehouse,
				item.qty,
				item.stock_qty,
				item.net_amount,
				item.base_net_amount
			from `tabSales Invoice Item` item
			inner join `tabSales Invoice` doc on doc.name = item.parent
			where doc.docstatus = 1
				and doc.update_stock = 1
				{date_clause}
				{electrician_clause}
				{item_clause}
				{item_group_clause}
		) sales_items
		order by sales_items.posting_date desc, sales_items.voucher_no desc
		""".format(
			date_clause=_date_clause(filters),
			electrician_clause=_equals_clause("doc.custom_electrician", filters.get("electrician")),
			item_clause=_equals_clause("item.item_code", filters.get("item_code") or filters.get("product")),
			item_group_clause=_equals_clause("item.item_group", filters.get("item_group")),
		),
		_get_date_params(filters)
		+ _get_equals_params(filters.get("electrician"))
		+ _get_equals_params(filters.get("item_code") or filters.get("product"))
		+ _get_equals_params(filters.get("item_group"))
		+ _get_date_params(filters)
		+ _get_equals_params(filters.get("electrician"))
		+ _get_equals_params(filters.get("item_code") or filters.get("product"))
		+ _get_equals_params(filters.get("item_group")),
		as_dict=True,
	)


def _get_doc_filters(filters):
	doc_filters = {"docstatus": 1}
	if filters.get("from_date") and filters.get("to_date"):
		doc_filters["posting_date"] = ["between", [filters.from_date, filters.to_date]]
	elif filters.get("from_date"):
		doc_filters["posting_date"] = [">=", filters.from_date]
	elif filters.get("to_date"):
		doc_filters["posting_date"] = ["<=", filters.to_date]

	if filters.get("electrician"):
		doc_filters["custom_electrician"] = filters.electrician

	return doc_filters


def _date_clause(filters):
	if filters.get("from_date") and filters.get("to_date"):
		return "and doc.posting_date between %s and %s"
	if filters.get("from_date"):
		return "and doc.posting_date >= %s"
	if filters.get("to_date"):
		return "and doc.posting_date <= %s"
	return ""


def _get_date_params(filters):
	if filters.get("from_date") and filters.get("to_date"):
		return [filters.from_date, filters.to_date]
	if filters.get("from_date"):
		return [filters.from_date]
	if filters.get("to_date"):
		return [filters.to_date]
	return []


def _equals_clause(column_name, value):
	return f"and {column_name} = %s" if value else ""


def _get_equals_params(value):
	return [value] if value else []

