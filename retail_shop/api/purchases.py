import frappe

from retail_shop.setup.defaults import SHOP_ADMIN_ROLE, TECHNICAL_ADMIN_ROLE


@frappe.whitelist()
def make_purchase_entry(payload: str):
	# Purchase Entry doctype permission already blocks Salesperson, but every
	# other whitelisted endpoint in this app declares its own role check
	# explicitly rather than relying solely on the permission map staying
	# correct — do the same here.
	frappe.only_for(("Administrator", TECHNICAL_ADMIN_ROLE, SHOP_ADMIN_ROLE))
	data = frappe.parse_json(payload)
	doc = frappe.get_doc({"doctype": "Purchase Entry", **data})
	doc.insert()
	return {"name": doc.name}

