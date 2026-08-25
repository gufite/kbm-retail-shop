import frappe

from frappe.desk.desktop import get_workspace_sidebar_items as core_get_workspace_sidebar_items

from retail_shop.setup.defaults import SHOP_ADMIN_ROLE, SALESPERSON_ROLE, is_technical_admin
from retail_shop.setup.workspace import SETTINGS_WORKSPACE_NAME, STAFF_WORKSPACE_NAME, WORKSPACE_NAME


@frappe.whitelist()
def get_workspace_sidebar_items():
	data = core_get_workspace_sidebar_items()
	roles = set(frappe.get_roles())

	if not (
		is_technical_admin(roles) or roles.intersection({SHOP_ADMIN_ROLE, SALESPERSON_ROLE})
	):
		return data

	visible_workspaces = {WORKSPACE_NAME}
	if is_technical_admin(roles) or SHOP_ADMIN_ROLE in roles:
		visible_workspaces.add(STAFF_WORKSPACE_NAME)
		visible_workspaces.add(SETTINGS_WORKSPACE_NAME)

	data["pages"] = [
		page
		for page in data.get("pages", [])
		if page.get("public") and page.get("name") in visible_workspaces
	]
	# Administrator has every role, including Workspace Manager. That flag
	# makes the desk show hidden ERPNext workspaces again; keep it off.
	data["has_access"] = 0
	data["has_create_access"] = 0
	return data
