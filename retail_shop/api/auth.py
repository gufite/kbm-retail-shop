from urllib.parse import urlencode

import frappe
from frappe.auth import LoginManager
from frappe.twofactor import should_run_2fa
from frappe.www.login import sanitize_redirect


@frappe.whitelist(allow_guest=True)
def browser_login(usr: str | None = None, pwd: str | None = None, redirect_to: str | None = None):
	redirect_to = sanitize_redirect(redirect_to) or "/app"

	try:
		login_manager = frappe.local.login_manager
		if not isinstance(login_manager, LoginManager):
			login_manager = frappe.local.login_manager = LoginManager()

		login_manager.authenticate(user=usr, pwd=pwd)

		if should_run_2fa(login_manager.user):
			_redirect_with_error("2fa_required", redirect_to)
			return

		login_manager.post_login()

		location = (
			frappe.local.response.get("redirect_to")
			or frappe.local.response.get("home_page")
			or redirect_to
		)
		frappe.local.response["type"] = "redirect"
		frappe.local.response["location"] = _absolute_location(location)
	except frappe.AuthenticationError:
		_redirect_with_error("invalid_credentials", redirect_to, usr)


def _redirect_with_error(error: str, redirect_to: str, usr: str | None = None):
	query = {"error": error, "redirect_to": redirect_to}
	if usr:
		query["usr"] = usr

	frappe.local.response["type"] = "redirect"
	frappe.local.response["location"] = _absolute_location(f"/retail-login?{urlencode(query)}")


def _absolute_location(path: str):
	if path.startswith(("http://", "https://")):
		return path

	return frappe.utils.get_url(path)
