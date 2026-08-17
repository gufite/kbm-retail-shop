import frappe

from frappe.desk.desktop import get_workspace_sidebar_items as core_get_workspace_sidebar_items

from retail_shop.setup.defaults import RETAIL_ADMIN_ROLE, RETAIL_SALESPERSON_ROLE
from retail_shop.setup.workspace import SETTINGS_WORKSPACE_NAME, WORKSPACE_NAME


@frappe.whitelist()
def get_workspace_sidebar_items():
	data = core_get_workspace_sidebar_items()
	roles = set(frappe.get_roles())

	if not roles.intersection({RETAIL_ADMIN_ROLE, RETAIL_SALESPERSON_ROLE}):
		return data

	# Staff (User management) is deliberately left out here: it's
	# technical-admin-only (System Manager), never shown to either retail
	# role regardless of admin/salesperson status.
	visible_workspaces = {WORKSPACE_NAME}
	if RETAIL_ADMIN_ROLE in roles:
		visible_workspaces.add(SETTINGS_WORKSPACE_NAME)

	data["pages"] = [
		page
		for page in data.get("pages", [])
		if page.get("public") and page.get("name") in visible_workspaces
	]
	return data
