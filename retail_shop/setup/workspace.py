import json
from contextlib import contextmanager

import frappe

from retail_shop.setup.defaults import SHOP_ADMIN_ROLE, SALESPERSON_ROLE, TECHNICAL_ADMIN_ROLE


# This is the Workspace document's actual name — it drives the page's URL
# route (the sidebar link is built from a slug of this same value), not just
# its on-screen label, so renaming the visible shop name means renaming this
# document too (see ensure_workspace's rename-on-drift handling below), and
# every other reference to "the retail workspace" in this app (modules.py,
# retail_shop.bundle.js) must use this same constant rather than a duplicate
# hardcoded string, or they silently drift out of sync with the real route.
WORKSPACE_NAME = "KBM Lighting Trading"
WORKSPACE_MODULE = "Retail Shop"
STAFF_WORKSPACE_NAME = "Staff"
SETTINGS_WORKSPACE_NAME = "Store Settings"
SHOP_WORKSPACE_NAMES = (WORKSPACE_NAME, STAFF_WORKSPACE_NAME, SETTINGS_WORKSPACE_NAME)

# Names this workspace document has previously been renamed from — kept so
# ensure_workspace() self-heals a site that hasn't picked up a rename yet,
# instead of _sync_workspace silently creating a second, duplicate workspace
# under the new name (frappe.get_doc/exists treat `name` as a plain primary
# key, they don't know it used to be called something else).
_LEGACY_WORKSPACE_NAMES = ("Retail Shop",)


def _rename_workspace_if_needed():
	if frappe.db.exists("Workspace", WORKSPACE_NAME):
		return
	for legacy_name in _LEGACY_WORKSPACE_NAMES:
		if frappe.db.exists("Workspace", legacy_name):
			frappe.rename_doc("Workspace", legacy_name, WORKSPACE_NAME)
			return


def ensure_workspace():
	if not frappe.db.exists("Module Def", WORKSPACE_MODULE):
		return

	_rename_workspace_if_needed()

	_sync_workspace(
		name=WORKSPACE_NAME,
		icon="sell",
		sequence_id=0,
		content=_get_workspace_content(),
		shortcuts=[],
		links=_get_workspace_cards(),
		roles=("System Manager", TECHNICAL_ADMIN_ROLE, SHOP_ADMIN_ROLE, SALESPERSON_ROLE),
	)
	_sync_workspace(
		name=STAFF_WORKSPACE_NAME,
		icon="users",
		sequence_id=1,
		content=_get_staff_workspace_content(),
		shortcuts=[],
		links=_get_staff_cards(),
		# Simple Users page (username + role + password). Technical Admin can
		# assign all three shop roles; Shop Admin is limited to Salesperson.
		roles=("System Manager", TECHNICAL_ADMIN_ROLE, SHOP_ADMIN_ROLE),
	)
	_sync_workspace(
		name=SETTINGS_WORKSPACE_NAME,
		icon="setting",
		sequence_id=2,
		content=_get_settings_workspace_content(),
		shortcuts=[],
		links=_get_settings_cards(),
		roles=("System Manager", TECHNICAL_ADMIN_ROLE, SHOP_ADMIN_ROLE),
	)

	_hide_redundant_home_workspace()
	_hide_non_shop_workspaces()


def _sync_workspace(name, icon, sequence_id, content, shortcuts, links, roles):
	workspace = _get_workspace_doc(name)
	workspace.update(
		{
			"label": name,
			"title": name,
			"module": WORKSPACE_MODULE,
			"public": 1,
			"icon": icon,
			"hide_custom": 0,
			"is_hidden": 0,
			"sequence_id": sequence_id,
			"content": json.dumps(content),
		}
	)

	workspace.set("shortcuts", [])
	for shortcut in shortcuts:
		workspace.append("shortcuts", shortcut)

	workspace.set("links", [])
	for card in links:
		workspace.append(
			"links",
			{
				"label": card["label"],
				"type": "Card Break",
				"description": card.get("description"),
				"icon": card.get("icon"),
				"hidden": 0,
				"link_count": len(card.get("links", [])),
			},
		)
		for link in card.get("links", []):
			workspace.append(
				"links",
				{
					"label": link["label"],
					"type": "Link",
					"link_type": link["link_type"],
					"link_to": link["link_to"],
					"is_query_report": link.get("is_query_report", 0),
					"report_ref_doctype": link.get("report_ref_doctype"),
				},
			)

	workspace.set("roles", [])
	for role in roles:
		workspace.append("roles", {"role": role})

	workspace.flags.ignore_permissions = True
	with _public_workspace_write():
		if workspace.is_new():
			workspace.insert(ignore_permissions=True)
		else:
			workspace.save(ignore_permissions=True)


def _get_workspace_doc(name):
	if frappe.db.exists("Workspace", name):
		return frappe.get_doc("Workspace", name)

	return frappe.get_doc({"doctype": "Workspace"})


def _hide_redundant_home_workspace():
	"""Keep the retail workspace as the single top-level landing page."""
	if not frappe.db.exists("Workspace", "Home"):
		return

	home_workspace = frappe.get_doc("Workspace", "Home")
	if home_workspace.is_hidden:
		return

	home_workspace.is_hidden = 1
	home_workspace.flags.ignore_permissions = True
	with _public_workspace_write():
		home_workspace.save(ignore_permissions=True)


def _hide_non_shop_workspaces():
	"""Hide native ERPNext/Frappe workspaces so the shop desk only keeps
	KBM Lighting Trading, Staff, and Store Settings. Administrator still
	has Workspace Manager, which would otherwise keep showing hidden
	pages — the sidebar API turns that flag off as well."""
	for name in frappe.get_all("Workspace", filters={"public": 1}, pluck="name"):
		if name in SHOP_WORKSPACE_NAMES:
			continue
		if frappe.db.get_value("Workspace", name, "is_hidden"):
			continue
		frappe.db.set_value("Workspace", name, "is_hidden", 1, update_modified=False)


def _get_workspace_content():
	return [
		{
			"id": "retail-shop-card-sales-counter",
			"type": "card",
			"data": {"card_name": "Sales Counter", "col": 3},
		},
		{
			"id": "retail-shop-card-back-office",
			"type": "card",
			"data": {"card_name": "Back Office", "col": 3},
		},
		{
			"id": "retail-shop-card-reports-audit",
			"type": "card",
			"data": {"card_name": "Reports & Audit", "col": 3},
		},
		{
			"id": "retail-shop-card-catalog-contacts",
			"type": "card",
			"data": {"card_name": "Catalog & Contacts", "col": 3},
		},
	]


def _get_workspace_cards():
	return [
		{
			"label": "Sales Counter",
			"links": [
				{"label": "Point of Sale", "link_type": "Page", "link_to": "point-of-sale"},
				{"label": "Counter Sales", "link_type": "DocType", "link_to": "POS Invoice"},
				{"label": "Sales Invoice", "link_type": "DocType", "link_to": "Sales Invoice"},
				{"label": "Stock Balance", "link_type": "Page", "link_to": "stock-balance"},
			],
		},
		{
			"label": "Back Office",
			"links": [
				{"label": "Stock In", "link_type": "DocType", "link_to": "Purchase Entry"},
				{
					"label": "Stock Count",
					"link_type": "DocType",
					"link_to": "Stock Reconciliation",
				},
				{"label": "Commission Payment", "link_type": "DocType", "link_to": "Commission Payment"},
			],
		},
		{
			"label": "Reports & Audit",
			"links": [
				{"label": "Sales Report", "link_type": "Report", "link_to": "Sales Report"},
				{"label": "Profit Report", "link_type": "Report", "link_to": "Profit Report"},
				{"label": "Inventory Valuation", "link_type": "Report", "link_to": "Inventory Valuation"},
				{
					"label": "Customer Balance Report",
					"link_type": "Report",
					"link_to": "Customer Balance Report",
				},
				{
					"label": "Supplier Balance Report",
					"link_type": "Report",
					"link_to": "Supplier Balance Report",
				},
				{"label": "Purchase Report", "link_type": "Report", "link_to": "Purchase Report"},
				{
					"label": "Electrician Commission Report",
					"link_type": "Report",
					"link_to": "Electrician Commission Report",
				},
				{"label": "Retail Audit Log", "link_type": "DocType", "link_to": "Retail Audit Log"},
			],
		},
		{
			"label": "Catalog & Contacts",
			"links": [
				{"label": "Products", "link_type": "DocType", "link_to": "Item"},
				{"label": "Categories", "link_type": "DocType", "link_to": "Item Group"},
				{"label": "Electrician", "link_type": "DocType", "link_to": "Electrician"},
				{"label": "Customer", "link_type": "DocType", "link_to": "Customer"},
				{"label": "Supplier", "link_type": "DocType", "link_to": "Supplier"},
			],
		},
	]


def _get_staff_workspace_content():
	return [
		{
			"id": "staff-card-management",
			"type": "card",
			"data": {"card_name": "Staff Management", "col": 12},
		},
	]


def _get_staff_cards():
	return [
		{
			"label": "Staff Management",
			"links": [
				{"label": "Users", "link_type": "Page", "link_to": "shop-users"},
			],
		},
	]


def _get_settings_workspace_content():
	return [
		{
			"id": "store-settings-card-configuration",
			"type": "card",
			"data": {"card_name": "Store Configuration", "col": 12},
		},
	]


def _get_settings_cards():
	return [
		{
			"label": "Store Configuration",
			"links": [
				{"label": "Retail Shop Settings", "link_type": "DocType", "link_to": "Retail Shop Settings"},
				{
					"label": "Retail Commission Settings",
					"link_type": "DocType",
					"link_to": "Retail Commission Settings",
				},
				{"label": "Mode of Payment", "link_type": "DocType", "link_to": "Mode of Payment"},
			],
		},
	]


@contextmanager
def _public_workspace_write():
	previous = frappe.flags.in_migrate
	frappe.flags.in_migrate = True
	try:
		yield
	finally:
		frappe.flags.in_migrate = previous
