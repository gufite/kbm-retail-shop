import frappe
from frappe import _
from frappe.utils import flt
from frappe.utils.synchronization import filelock

from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_mode_of_payment_info

from retail_shop.utils.sales import get_payment_method_label

# get_sale_summary only ever needs to read these two — never let the
# doctype come from the caller unchecked (see below).
_SALE_SUMMARY_DOCTYPES = ("Sales Invoice", "POS Invoice")


@frappe.whitelist()
def record_credit_payments(invoice_name: str, payments: str):
	"""Collect a credit sale's outstanding balance, optionally split across
	multiple payment methods in one call, e.g. part cash + part mobile money."""
	frappe.only_for(("Administrator", "Technical Admin", "Shop Admin", "Salesperson"))
	rows = frappe.parse_json(payments)
	if not rows:
		frappe.throw(_("At least one payment is required."))

	# Serialize per invoice: two near-simultaneous collection attempts
	# against the same credit sale could otherwise both read the same
	# outstanding_amount before either commits, and both pass the check,
	# overpaying the invoice. See commission_payment.py for the same pattern
	# (and why a plain file lock, not a distributed one, fits this app).
	with filelock(f"credit-payment-{invoice_name}", timeout=10):
		invoice = frappe.get_doc("Sales Invoice", invoice_name)
		total = sum(flt(row.get("amount")) for row in rows)
		if total > flt(invoice.outstanding_amount) + 0.005:
			frappe.throw(_("Payment amount exceeds the invoice's outstanding balance."))

		created = [_create_payment_entry(invoice, row["mode_of_payment"], flt(row["amount"])) for row in rows]
		frappe.db.commit()

	return {"payment_entries": created}


def _create_payment_entry(invoice, mode_of_payment: str, amount: float) -> str:
	payment_details = get_mode_of_payment_info(mode_of_payment, invoice.company)
	payment = get_payment_entry(
		"Sales Invoice",
		invoice.name,
		party_amount=amount,
		bank_account=payment_details.default_account,
	)
	payment.mode_of_payment = mode_of_payment
	payment.paid_amount = amount
	payment.received_amount = amount
	payment.insert()
	payment.submit()
	return payment.name


@frappe.whitelist()
def get_sale_summary(doctype: str, name: str):
	frappe.only_for(("Administrator", "Technical Admin", "Shop Admin", "Salesperson"))
	if doctype not in _SALE_SUMMARY_DOCTYPES:
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	doc = frappe.get_doc(doctype, name)
	doc.check_permission("read")
	return {
		"name": doc.name,
		"doctype": doc.doctype,
		"grand_total": doc.grand_total,
		"net_total": doc.net_total,
		"outstanding_amount": doc.outstanding_amount,
		"payment_method": get_payment_method_label(doc),
		"commission_amount": doc.custom_commission_amount,
	}

