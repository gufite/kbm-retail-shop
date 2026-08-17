import frappe


# Every doctype linked from the shop's own workspace (workspace.WORKSPACE_NAME
# / SETTINGS_WORKSPACE_NAME) — everywhere a salesperson/admin lands on a list
# view as part of the SRS workflow (Sec. 12: "simple, fast, user-friendly").
# The generic Frappe social features (comment count, like) are noise for a
# single-shop retail tool and are hidden here rather than left to default
# desk chrome. Disabling disable_comment_count also removes the "·" separator
# next to it (list_view.js only renders that separator when a comment count
# is shown) and, combined with the like-hiding CSS in retail_shop.bundle.css,
# leaves a clean list row with just the modified time.
LIST_VIEWS_WITHOUT_SOCIAL_FEATURES = (
	"Item",
	"POS Invoice",
	"Sales Invoice",
	"Purchase Receipt",
	"Purchase Entry",
	"Stock Reconciliation",
	"Commission Payment",
	"Retail Audit Log",
	"Electrician",
	"Customer",
	"Supplier",
	"Warehouse",
	"Mode of Payment",
)


def ensure_list_view_settings():
	for doctype in LIST_VIEWS_WITHOUT_SOCIAL_FEATURES:
		if frappe.db.exists("List View Settings", doctype):
			frappe.db.set_value("List View Settings", doctype, "disable_comment_count", 1)
		else:
			frappe.get_doc(
				{
					"doctype": "List View Settings",
					"name": doctype,
					"disable_comment_count": 1,
				}
			).insert(ignore_permissions=True)
