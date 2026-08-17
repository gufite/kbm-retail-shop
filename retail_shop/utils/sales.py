import frappe
from frappe import _
from frappe.utils import cint, flt

from retail_shop.utils.audit import log_audit_event


RETAIL_SALES_DOCTYPES = {"POS Invoice", "Sales Invoice"}


def validate_sales_doc(doc, method=None):
	if not _is_managed_sales_doc(doc):
		return

	settings = frappe.get_cached_doc("Retail Shop Settings")
	if not doc.is_return:
		_set_default_customer(doc, settings)

	_validate_electrician(doc, settings)
	_validate_customer_for_credit_sale(doc, settings)


def before_submit_sales_doc(doc, method=None):
	if not _is_managed_sales_doc(doc):
		return

	if doc.is_return:
		apply_return_commission_snapshot(doc)
	else:
		apply_sale_commission_snapshot(doc)


def on_cancel_sales_doc(doc, method=None):
	if not _is_managed_sales_doc(doc):
		return

	if not doc.custom_electrician:
		return

	log_audit_event(
		event_type="Sale Cancelled",
		reference_doctype=doc.doctype,
		reference_name=doc.name,
		details=_("Sale for electrician {0} cancelled; commission of {1} no longer counts toward any report or dashboard total.").format(
			doc.custom_electrician, doc.custom_commission_amount
		),
	)


def apply_sale_commission_snapshot(doc):
	precision = _get_currency_precision(doc)

	if not doc.custom_electrician:
		doc.custom_commission_type = None
		doc.custom_commission_rate = 0
		doc.custom_commission_basis_amount = 0
		doc.custom_commission_amount = 0
		return

	commission_type, rate = _resolve_commission_rate(doc.custom_electrician)
	basis_amount = _get_commission_basis_amount(doc)
	commission_amount = (
		flt(basis_amount * rate / 100, precision) if commission_type == "Percentage" else flt(rate, precision)
	)
	doc.custom_commission_type = commission_type
	doc.custom_commission_rate = rate
	doc.custom_commission_basis_amount = flt(basis_amount, precision)
	doc.custom_commission_amount = commission_amount


def _resolve_commission_rate(electrician: str):
	electrician_doc = frappe.get_cached_doc("Electrician", electrician)
	if electrician_doc.commission_type:
		rate = (
			electrician_doc.commission_percentage
			if electrician_doc.commission_type == "Percentage"
			else electrician_doc.fixed_commission_amount
		)
		return electrician_doc.commission_type, flt(rate)

	settings = frappe.get_cached_doc("Retail Commission Settings")
	commission_type = settings.commission_type or "Percentage"
	rate = flt(settings.commission_percentage if commission_type == "Percentage" else settings.fixed_commission_amount)
	return commission_type, rate


def apply_return_commission_snapshot(doc):
	if not doc.return_against:
		frappe.throw(_("A return must reference the original sale."))

	original = frappe.get_doc(doc.doctype, doc.return_against)
	precision = _get_currency_precision(doc)
	original_basis = abs(flt(original.custom_commission_basis_amount or _get_commission_basis_amount(original)))
	current_basis = abs(flt(_get_commission_basis_amount(doc)))
	# Clamped to 1: a return basis larger than the original sale's (e.g. a
	# return row edited to a bigger qty/amount than what was actually sold)
	# must not reverse MORE commission than was ever earned on the original.
	ratio = min(flt(current_basis / original_basis, 6), 1) if original_basis else 0
	reversal_amount = flt(abs(flt(original.custom_commission_amount)) * ratio, precision)

	doc.custom_electrician = doc.custom_electrician or original.custom_electrician
	doc.custom_commission_type = original.custom_commission_type
	doc.custom_commission_rate = original.custom_commission_rate
	doc.custom_commission_basis_amount = flt(-current_basis, precision)
	doc.custom_commission_amount = flt(-reversal_amount, precision)


def get_payment_method_label(doc) -> str:
	payment_methods = []
	for row in doc.get("payments") or []:
		if row.mode_of_payment and row.mode_of_payment not in payment_methods:
			payment_methods.append(row.mode_of_payment)

	if payment_methods:
		return ", ".join(payment_methods)

	if doc.doctype == "Sales Invoice" and flt(doc.outstanding_amount) > 0:
		return "Credit"

	if doc.doctype == "POS Invoice" and flt(doc.outstanding_amount) > 0:
		return "Credit"

	return "Unspecified"


def is_credit_sale(doc) -> bool:
	return doc.doctype == "Sales Invoice" and flt(doc.outstanding_amount) > 0


def _is_managed_sales_doc(doc) -> bool:
	if doc.doctype not in RETAIL_SALES_DOCTYPES:
		return False
	return doc.doctype == "POS Invoice" or cint(doc.get("update_stock"))


def _set_default_customer(doc, settings):
	if doc.customer:
		return
	if settings.default_walk_in_customer:
		doc.customer = settings.default_walk_in_customer


def _validate_electrician(doc, settings):
	require_electrician = cint(settings.require_electrician)
	if doc.is_return:
		return

	if require_electrician and not doc.custom_electrician:
		frappe.throw(_("Electrician is required before the sale can be submitted."))

	if doc.custom_electrician:
		active = frappe.db.get_value("Electrician", doc.custom_electrician, "active")
		if not active:
			frappe.throw(_("Electrician {0} is inactive.").format(frappe.bold(doc.custom_electrician)))


def _validate_customer_for_credit_sale(doc, settings):
	if doc.is_return:
		return

	is_credit = flt(doc.outstanding_amount) > 0.005
	if is_credit and settings.default_walk_in_customer and doc.customer == settings.default_walk_in_customer:
		frappe.throw(_("A credit sale must have a real customer selected, not the walk-in customer."))


def _get_currency_precision(doc) -> int:
	return doc.precision("grand_total") or 2


def _get_commission_basis_amount(doc) -> float:
	# Commission is based on the final, discounted sale amount excluding tax —
	# net_total alone misses order-level discounts applied on Grand Total.
	return flt(doc.grand_total) - flt(doc.total_taxes_and_charges or 0)

