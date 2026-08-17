import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


# The Item form ships with several ERPNext tabs this single-shop retail app
# never uses: Manufacturing (BOMs/sub-contracting), Quality (inspection
# templates), and Purchasing (native supplier/last-purchase-rate fields —
# superseded here by the custom Purchase Entry doctype, which doesn't read
# from this tab at all). Hiding them keeps the Item form aligned with what
# the SRS actually asks for (Sec. 12: simple, fast, user-friendly).
HIDDEN_ITEM_TABS = ("manufacturing", "quality_tab", "purchasing_tab")


def ensure_item_form_tabs_hidden():
	for fieldname in HIDDEN_ITEM_TABS:
		name = f"Item-{fieldname}-hidden"
		if frappe.db.exists("Property Setter", name):
			frappe.db.set_value("Property Setter", name, "value", "1")
			continue
		make_property_setter("Item", fieldname, "hidden", "1", "Check")
