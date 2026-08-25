import frappe
from frappe.permissions import add_permission, update_permission_property

from retail_shop.setup.defaults import SHOP_ADMIN_ROLE, SALESPERSON_ROLE, TECHNICAL_ADMIN_ROLE


PERM_TYPES = (
	"read",
	"create",
	"write",
	"delete",
	"submit",
	"cancel",
	"amend",
	"report",
	"print",
	"email",
	"share",
	"export",
)


def ensure_permissions():
	for doctype, rules in _permission_map().items():
		for role, permissions in rules.items():
			ensure_doctype_permission(doctype, role, permissions)
	ensure_page_access()


# Frappe's Desk "Page" records (distinct from doctype permissions) gate a few
# standard screens by their own hardcoded role list — POS Invoice's own
# doctype permissions don't matter if the Point of Sale *page* itself
# rejects the role first. Add our roles wherever the SRS needs that page.
PAGE_ACCESS = {
	"point-of-sale": (TECHNICAL_ADMIN_ROLE, SHOP_ADMIN_ROLE, SALESPERSON_ROLE),
	"stock-balance": (TECHNICAL_ADMIN_ROLE, SHOP_ADMIN_ROLE, SALESPERSON_ROLE),
	# Shop user management (username + role + password). Technical Admin
	# can assign all three shop roles; Shop Admin is limited to Salesperson
	# in the API even though they can open the same page.
	"shop-users": (TECHNICAL_ADMIN_ROLE, SHOP_ADMIN_ROLE),
	"sales-staff": (TECHNICAL_ADMIN_ROLE, SHOP_ADMIN_ROLE),
}


def ensure_page_access():
	for page_name, roles in PAGE_ACCESS.items():
		if not frappe.db.exists("Page", page_name):
			continue
		page = frappe.get_doc("Page", page_name)
		existing = {row.role for row in page.roles}
		for role in roles:
			if role not in existing:
				page.append("roles", {"role": role})
		page.flags.ignore_permissions = True
		page.save(ignore_permissions=True)


def ensure_doctype_permission(doctype: str, role: str, permissions: dict[str, int]):
	add_permission(doctype, role, 0)
	# Set every permission type explicitly (defaulting to 0) so re-running this on
	# migrate is authoritative: a right removed from the map below is actually
	# revoked, not just left over from a previous migrate.
	for perm_type in PERM_TYPES:
		update_permission_property(doctype, role, 0, perm_type, permissions.get(perm_type, 0))


def _permission_map():
	admin_full = {
		"read": 1,
		"create": 1,
		"write": 1,
		"delete": 1,
		"submit": 1,
		"cancel": 1,
		"amend": 1,
		"report": 1,
		"print": 1,
		"email": 1,
		"share": 1,
		"export": 1,
	}
	return {
		"Electrician": {
			SHOP_ADMIN_ROLE: admin_full,
			SALESPERSON_ROLE: {"read": 1, "report": 1},
		},
		"Retail Commission Settings": {
			SHOP_ADMIN_ROLE: admin_full,
		},
		"Retail Shop Settings": {
			SHOP_ADMIN_ROLE: admin_full,
		},
		"Purchase Entry": {
			SHOP_ADMIN_ROLE: admin_full,
		},
		"Company": {
			# Read-only: needed to select the company in the standard POS
			# opening-shift dialog. Company management itself isn't an
			# SRS admin task, so no write access.
			SHOP_ADMIN_ROLE: {"read": 1},
			SALESPERSON_ROLE: {"read": 1},
		},
		# Read-only master-data lookups the Sales/POS Invoice engine itself
		# needs (default accounts, currency, cost center, valuation
		# settings) — none of these are SRS-level admin tasks, so read
		# only, same as Company above.
		"Stock Settings": {
			SHOP_ADMIN_ROLE: {"read": 1},
			SALESPERSON_ROLE: {"read": 1},
		},
		"Currency": {
			SHOP_ADMIN_ROLE: {"read": 1},
			SALESPERSON_ROLE: {"read": 1},
		},
		"Account": {
			SHOP_ADMIN_ROLE: {"read": 1},
			SALESPERSON_ROLE: {"read": 1},
		},
		"Cost Center": {
			SHOP_ADMIN_ROLE: {"read": 1},
			SALESPERSON_ROLE: {"read": 1},
		},
		"POS Settings": {
			SHOP_ADMIN_ROLE: {"read": 1},
			SALESPERSON_ROLE: {"read": 1},
		},
		"Mode of Payment": {
			SHOP_ADMIN_ROLE: {"read": 1},
			SALESPERSON_ROLE: {"read": 1},
		},
		"UOM": {
			SHOP_ADMIN_ROLE: admin_full,
			SALESPERSON_ROLE: {"read": 1},
		},
		"Item Group": {
			SHOP_ADMIN_ROLE: admin_full,
			SALESPERSON_ROLE: {"read": 1, "report": 1},
		},
		"Brand": {
			SHOP_ADMIN_ROLE: admin_full,
			SALESPERSON_ROLE: {"read": 1},
		},
		"Item Tax Template": {
			SHOP_ADMIN_ROLE: admin_full,
			SALESPERSON_ROLE: {"read": 1},
		},
		"Price List": {
			SHOP_ADMIN_ROLE: {"read": 1},
			SALESPERSON_ROLE: {"read": 1},
		},
		"Item Price": {
			SHOP_ADMIN_ROLE: {"read": 1},
			SALESPERSON_ROLE: {"read": 1},
		},
		# Workspace layout (the "KBM Lighting Trading" home screen and its
		# tabs/cards) is technical/developer-owned, not a shop-admin task —
		# every logged-in desk user gets full Workspace create/write/delete
		# by default via the standard "Desk User" role, so an explicit
		# Custom DocPerm override here is the only way to actually take
		# that away from our roles (see ensure_doctype_permission — once any
		# Custom DocPerm exists for a doctype, Frappe stops looking at its
		# standard DocPerm rows entirely, so System Manager/Workspace
		# Manager need their own explicit rows here too, not just ours).
		"Workspace": {
			"System Manager": admin_full,
			"Workspace Manager": admin_full,
			# Standard Frappe grants every logged-in desk user (via the
			# baseline "Desk User" role everyone gets) full create/write/
			# delete on Workspace by default — reset that back to read-only
			# here too, or it silently survives as a leftover Custom DocPerm
			# row underneath our own roles below.
			"Desk User": {"read": 1},
			TECHNICAL_ADMIN_ROLE: {"read": 1},
			SHOP_ADMIN_ROLE: {"read": 1},
			SALESPERSON_ROLE: {"read": 1},
		},
		# Customer Group / Territory: the Customer quick-entry dialog on the
		# POS screen requires read on both to populate/select them, even
		# though a salesperson never manages the groups/territories themselves.
		"Customer Group": {
			SHOP_ADMIN_ROLE: {"read": 1},
			SALESPERSON_ROLE: {"read": 1},
		},
		"Territory": {
			SHOP_ADMIN_ROLE: {"read": 1},
			SALESPERSON_ROLE: {"read": 1},
		},
		"Page": {
			# Generic doctype-level read is required in addition to the
			# specific page's own Has Role list (see ensure_page_access) —
			# without this, a "Page"-type workspace shortcut (e.g. our
			# Point of Sale shortcut) is silently dropped from the
			# permission-filtered shortcut list even though the page
			# itself is directly reachable by URL.
			"System Manager": {"read": 1},
			TECHNICAL_ADMIN_ROLE: {"read": 1},
			SHOP_ADMIN_ROLE: {"read": 1},
			SALESPERSON_ROLE: {"read": 1},
		},
		"POS Profile": {
			SHOP_ADMIN_ROLE: {"read": 1},
			SALESPERSON_ROLE: {"read": 1},
		},
		# Needed by api.sales.record_credit_payments, which creates and
		# submits a Payment Entry against a credit Sales Invoice — without
		# this, that whitelisted call throws a PermissionError for every
		# caller (neither role had any grant on this doctype before).
		"Payment Entry": {
			SHOP_ADMIN_ROLE: admin_full,
			SALESPERSON_ROLE: {
				# No cancel/amend: only an Administrator may void or correct a completed payment.
				"read": 1,
				"create": 1,
				"submit": 1,
				"report": 1,
				"print": 1,
				"email": 1,
			},
		},
		"POS Opening Entry": {
			SHOP_ADMIN_ROLE: admin_full,
			SALESPERSON_ROLE: {"read": 1, "create": 1, "write": 1, "submit": 1},
		},
		"POS Closing Entry": {
			SHOP_ADMIN_ROLE: admin_full,
			SALESPERSON_ROLE: {"read": 1, "create": 1, "write": 1, "submit": 1},
		},
		"POS Invoice": {
			SHOP_ADMIN_ROLE: admin_full,
			SALESPERSON_ROLE: {
				# No cancel/amend: only an Administrator may void or correct a completed sale.
				"read": 1,
				"create": 1,
				"write": 1,
				"submit": 1,
				"report": 1,
				"print": 1,
				"email": 1,
			},
		},
		"Sales Invoice": {
			SHOP_ADMIN_ROLE: admin_full,
			SALESPERSON_ROLE: {
				# No cancel/amend: only an Administrator may void or correct a completed sale.
				"read": 1,
				"create": 1,
				"write": 1,
				"submit": 1,
				"report": 1,
				"print": 1,
				"email": 1,
			},
		},
		"Item": {
			SHOP_ADMIN_ROLE: admin_full,
			SALESPERSON_ROLE: {"read": 1, "report": 1, "print": 1, "export": 1},
		},
		"Warehouse": {
			SHOP_ADMIN_ROLE: admin_full,
			SALESPERSON_ROLE: {"read": 1, "report": 1, "print": 1},
		},
		"Supplier": {
			SHOP_ADMIN_ROLE: admin_full,
			SALESPERSON_ROLE: {"read": 1},
		},
		"Customer": {
			SHOP_ADMIN_ROLE: admin_full,
			SALESPERSON_ROLE: {"read": 1, "create": 1, "write": 1},
		},
		"Purchase Receipt": {
			SHOP_ADMIN_ROLE: admin_full,
		},
		"Stock Reconciliation": {
			SHOP_ADMIN_ROLE: admin_full,
		},
		"Commission Payment": {
			SHOP_ADMIN_ROLE: admin_full,
			SALESPERSON_ROLE: {"read": 1, "report": 1, "print": 1, "email": 1},
		},
		"Retail Audit Log": {
			# Append-only: rows are only ever written by our own hooks via
			# ignore_permissions, so no role gets create/write here — not even Admin.
			SHOP_ADMIN_ROLE: {"read": 1, "report": 1, "print": 1, "export": 1},
		},
	}

