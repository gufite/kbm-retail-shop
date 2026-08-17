app_name = "retail_shop"
app_title = "KBM Lighting Trading"
app_publisher = "name-1"
app_description = "Sales and Inventory Management System"
app_email = "admin@example.com"
app_license = "mit"

required_apps = ["erpnext"]

app_include_css = "retail_shop.bundle.css"
app_include_js = "retail_shop.bundle.js"
app_logo_url = "/assets/retail_shop/images/kbm-logo.png"
boot_session = "retail_shop.startup.boot.boot_session"
website_route_rules = [
	{"from_route": "/login", "to_route": "retail-login"},
	# The custom retail-login form has no 2FA UI of its own; this keeps
	# Frappe's stock login page (which handles the OTP step) reachable as
	# a fallback for 2FA-enabled users instead of dead-ending them.
	{"from_route": "/login-2fa", "to_route": "login"},
]
override_whitelisted_methods = {
	"frappe.desk.desktop.get_workspace_sidebar_items": "retail_shop.api.workspace.get_workspace_sidebar_items"
}

after_install = "retail_shop.setup.install.after_install"
after_migrate = "retail_shop.setup.install.after_migrate"
before_tests = "retail_shop.setup.install.before_tests"

doc_events = {
	"POS Invoice": {
		"validate": "retail_shop.utils.sales.validate_sales_doc",
		"before_submit": "retail_shop.utils.sales.before_submit_sales_doc",
		"on_cancel": "retail_shop.utils.sales.on_cancel_sales_doc",
	},
	"Sales Invoice": {
		"validate": "retail_shop.utils.sales.validate_sales_doc",
		"before_submit": "retail_shop.utils.sales.before_submit_sales_doc",
		"on_cancel": "retail_shop.utils.sales.on_cancel_sales_doc",
	},
	"Stock Reconciliation": {
		"validate": "retail_shop.utils.inventory.require_adjustment_reason",
		"on_submit": "retail_shop.utils.inventory.log_stock_adjustment",
	},
	"Retail Commission Settings": {
		"on_update": "retail_shop.utils.audit.log_commission_settings_change",
	},
	"Electrician": {
		"on_update": "retail_shop.utils.audit.log_electrician_commission_change",
	},
	"User": {
		"validate": "retail_shop.setup.modules.apply_module_profile_to_user",
		"on_update": [
			"retail_shop.utils.audit.log_user_role_change",
			"retail_shop.setup.modules.ensure_home_page_default",
		],
	},
}

scheduler_events = {
	"daily": [
		"retail_shop.utils.inventory.notify_stock_alerts",
	],
}
