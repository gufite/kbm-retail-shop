import frappe

from frappe.desk.desktop import get_workspace_sidebar_items as core_get_workspace_sidebar_items

from retail_shop.setup.defaults import SHOP_ADMIN_ROLE, SALESPERSON_ROLE, is_technical_admin
from retail_shop.setup.workspace import SETTINGS_WORKSPACE_NAME, WORKSPACE_NAME


@frappe.whitelist()
def get_workspace_sidebar_items():
	data = core_get_workspace_sidebar_items()
	roles = set(frappe.get_roles())

	if is_technical_admin(roles):
		return data

	if not roles.intersection({SHOP_ADMIN_ROLE, SALESPERSON_ROLE}):
		return data

	# Staff (raw User management) stays technical-admin-only.
	visible_workspaces = {WORKSPACE_NAME}
	if SHOP_ADMIN_ROLE in roles:
		visible_workspaces.add(SETTINGS_WORKSPACE_NAME)

	data["pages"] = [
		page
		for page in data.get("pages", [])
		if page.get("public") and page.get("name") in visible_workspaces
	]
	return data
