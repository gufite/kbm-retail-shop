import frappe
from frappe.utils import now_datetime

from retail_shop.setup.branding import ensure_branding
from retail_shop.setup.custom_fields import ensure_custom_fields
from retail_shop.setup.defaults import ensure_defaults
from retail_shop.setup.item_form import ensure_shop_forms
from retail_shop.setup.list_view import ensure_list_view_settings
from retail_shop.setup.modules import ensure_module_visibility
from retail_shop.setup.permissions import ensure_permissions
from retail_shop.setup.pos_fields import ensure_pos_invoice_fields
from retail_shop.setup.workspace import ensure_workspace


def ensure_retail_shop_setup():
	ensure_custom_fields()
	ensure_defaults()
	ensure_permissions()
	ensure_workspace()
	ensure_module_visibility()
	ensure_list_view_settings()
	ensure_shop_forms()
	ensure_pos_invoice_fields()
	ensure_branding()


def after_install():
	ensure_retail_shop_setup()


def after_migrate():
	ensure_retail_shop_setup()
	frappe.clear_cache()


def before_tests():
	_ensure_company_for_tests()
	ensure_retail_shop_setup()
	frappe.clear_cache()


def _ensure_company_for_tests():
	# retail_shop's setup only fills in defaults when a Company already exists
	# (e.g. via ERPNext's own setup wizard). Running this app's tests in
	# isolation (`bench run-tests --app retail_shop`) only fires this app's own
	# before_tests hook, not ERPNext's — so make sure base org data exists
	# regardless of test invocation order.
	if frappe.db.a_row_exists("Company"):
		return

	from frappe.desk.page.setup_wizard.setup_wizard import setup_complete

	current_year = now_datetime().year
	setup_complete(
		{
			"currency": "ETB",
			"full_name": "Test User",
			"company_name": "Retail Test Company",
			"timezone": "Africa/Addis_Ababa",
			"company_abbr": "RTC",
			"industry": "Retail & Wholesale",
			"country": "Ethiopia",
			"fy_start_date": f"{current_year}-01-01",
			"fy_end_date": f"{current_year}-12-31",
			"language": "english",
			"email": "test@example.com",
			"password": "test",
			"chart_of_accounts": "Standard",
		}
	)
