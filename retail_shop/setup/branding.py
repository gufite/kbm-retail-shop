import frappe


LOGO_URL = "/assets/retail_shop/images/kbm-logo.png"
APP_NAME = "KBM Lighting Trading"


def ensure_branding():
	_ensure_website_settings()
	_ensure_navbar_logo()
	_ensure_company_logo()


def _ensure_website_settings():
	settings = frappe.get_single("Website Settings")
	changed = False
	if settings.app_name != APP_NAME:
		settings.app_name = APP_NAME
		changed = True
	if settings.app_logo != LOGO_URL:
		settings.app_logo = LOGO_URL
		changed = True
	if settings.favicon != LOGO_URL:
		settings.favicon = LOGO_URL
		changed = True
	if changed:
		settings.flags.ignore_permissions = True
		settings.save()


def _ensure_navbar_logo():
	navbar = frappe.get_single("Navbar Settings")
	if navbar.app_logo != LOGO_URL:
		navbar.app_logo = LOGO_URL
		navbar.flags.ignore_permissions = True
		navbar.save()


def _ensure_company_logo():
	company = frappe.db.get_single_value("Retail Shop Settings", "default_company")
	if not company:
		return
	if frappe.db.get_value("Company", company, "company_logo") != LOGO_URL:
		frappe.db.set_value("Company", company, "company_logo", LOGO_URL)
