import frappe
from frappe import _
from frappe.utils import flt

from retail_shop.utils.reporting import get_sales_documents


def validate_commission_rate_fields(doc, type_required: bool):
	"""Shared by RetailCommissionSettings (global default, type always set)
	and Electrician (per-electrician override, blank type = "use global") —
	keeps the 0-100% cap and non-negative fixed amount in one place. Without
	the upper bound, a Percentage rate over 100 produces a commission larger
	than the sale itself (see sales.apply_sale_commission_snapshot)."""
	if doc.commission_type == "Percentage":
		if doc.commission_percentage is None and type_required:
			frappe.throw(_("Commission percentage is required."))
		if flt(doc.commission_percentage) < 0:
			frappe.throw(_("Commission percentage cannot be negative."))
		if flt(doc.commission_percentage) > 100:
			frappe.throw(_("Commission percentage cannot exceed 100%."))
		doc.fixed_commission_amount = 0
	elif doc.commission_type == "Fixed Amount":
		if doc.fixed_commission_amount is None and type_required:
			frappe.throw(_("Fixed commission amount is required."))
		if flt(doc.fixed_commission_amount) < 0:
			frappe.throw(_("Fixed commission amount cannot be negative."))
		doc.commission_percentage = 0
	elif type_required:
		frappe.throw(_("Commission Type is required."))
	else:
		# Electrician: blank commission_type means "no override" — leaves
		# resolution to fall through to Retail Commission Settings (see
		# sales._resolve_commission_rate), so both override fields are
		# meaningless here and should not carry stale values forward.
		doc.commission_percentage = 0
		doc.fixed_commission_amount = 0


def get_commission_earned(electrician: str = None, from_date: str = None, to_date: str = None) -> float:
	filters = {}
	if electrician:
		filters["electrician"] = electrician
	if from_date:
		filters["from_date"] = from_date
	if to_date:
		filters["to_date"] = to_date

	rows = get_sales_documents(filters)
	return flt(sum(row["commission_amount"] or 0 for row in rows if row["electrician"]))


def get_commission_paid(
	electrician: str = None, from_date: str = None, to_date: str = None, exclude: str = None
) -> float:
	filters = {"docstatus": 1}
	if electrician:
		filters["electrician"] = electrician
	if exclude:
		filters["name"] = ["!=", exclude]

	# A prior payment counts against this period if the period it was paid
	# FOR (its own from_date/to_date) overlaps the period being checked —
	# not when the payment was physically made (payment_date). Those are
	# unrelated: a payment made in February for January's commission has
	# payment_date=Feb but from_date/to_date=Jan, so filtering on
	# payment_date silently dropped it from "already paid" whenever the
	# check ran for a different period than the payment date fell in,
	# permitting the same period's commission to be paid out twice.
	if from_date and to_date:
		filters["from_date"] = ["<=", to_date]
		filters["to_date"] = [">=", from_date]
	elif from_date:
		filters["to_date"] = [">=", from_date]
	elif to_date:
		filters["from_date"] = ["<=", to_date]

	rows = frappe.get_all("Commission Payment", filters=filters, fields=["amount_paid"])
	return flt(sum(row.amount_paid for row in rows))


def get_commission_outstanding(electrician: str = None, from_date: str = None, to_date: str = None) -> float:
	earned = get_commission_earned(electrician, from_date, to_date)
	paid = get_commission_paid(electrician, from_date, to_date)
	return flt(earned - paid)


def get_total_commission_summary() -> dict:
	earned = get_commission_earned()
	paid = get_commission_paid()
	return {"earned": earned, "paid": paid, "outstanding": flt(earned - paid)}
