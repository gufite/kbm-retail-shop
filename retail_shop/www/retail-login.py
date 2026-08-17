import frappe
from frappe import _
from frappe.www.login import sanitize_redirect

no_cache = 1


def get_context(context):
	redirect_to = sanitize_redirect(
		frappe.form_dict.get("redirect_to") or frappe.form_dict.get("redirect-to")
	) or "/app"

	if frappe.session.user != "Guest":
		frappe.local.flags.redirect_location = redirect_to
		raise frappe.Redirect

	context.no_cache = 1
	context.title = _("KBM Lighting Trading Login")
	context.error = frappe.form_dict.get("error")
	context.redirect_to = redirect_to
	context.usr = frappe.form_dict.get("usr") or ""
