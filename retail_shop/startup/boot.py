import frappe

from retail_shop.setup.defaults import RETAIL_ADMIN_ROLE, RETAIL_SALESPERSON_ROLE
from retail_shop.setup.workspace import SETTINGS_WORKSPACE_NAME, STAFF_WORKSPACE_NAME, WORKSPACE_NAME


def boot_session(bootinfo):
	if frappe.session.user == "Guest":
		return

	roles = set(frappe.get_roles())
	if not roles.intersection({RETAIL_ADMIN_ROLE, RETAIL_SALESPERSON_ROLE}):
		return

	allowed_workspaces = list(bootinfo.get("allowed_workspaces") or [])
	workspace_by_name = {page.get("name"): page for page in allowed_workspaces}
	retail_workspace = workspace_by_name.get(WORKSPACE_NAME)

	if not retail_workspace:
		return

	home_alias = dict(retail_workspace)
	home_alias["name"] = "Home"
	home_alias["label"] = WORKSPACE_NAME

	visible_workspaces = [home_alias, retail_workspace]
	if RETAIL_ADMIN_ROLE in roles:
		for workspace_name in (STAFF_WORKSPACE_NAME, SETTINGS_WORKSPACE_NAME):
			workspace = workspace_by_name.get(workspace_name)
			if workspace:
				visible_workspaces.append(workspace)

	bootinfo.allowed_workspaces = visible_workspaces

	if bootinfo.user:
		bootinfo.user.default_workspace = {
			"name": WORKSPACE_NAME,
			"title": WORKSPACE_NAME,
			"public": 1,
		}
