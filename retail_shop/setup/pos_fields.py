import frappe

# POS Settings.invoice_fields is ERPNext's own extension point for the POS
# screen's "Additional Information" panel (erpnext/.../pos_payment.js) — it
# renders whatever fields are listed here against the in-progress POS
# Invoice, with edits written straight back to the doc. Without this, the
# custom_electrician/custom_commission_amount fields exist on the doctype
# but have no way to be seen or set from the actual POS screen a salesperson
# uses (SRS Sec. 3.1: electrician is optional per sale).
POS_INVOICE_FIELDS = (
	{
		"fieldname": "discount_amount",
		"label": "Transaction Discount",
		"fieldtype": "Currency",
	},
	{
		"fieldname": "custom_electrician",
		"label": "Electrician",
		"fieldtype": "Link",
		"options": "Electrician",
	},
	{
		"fieldname": "custom_commission_amount",
		"label": "Commission",
		"fieldtype": "Currency",
		"read_only": 1,
	},
)


def ensure_pos_invoice_fields():
	settings = frappe.get_single("POS Settings")
	existing = {row.fieldname: row for row in settings.invoice_fields}
	changed = False
	for field in POS_INVOICE_FIELDS:
		if field["fieldname"] in existing:
			row = existing[field["fieldname"]]
			for key, value in field.items():
				if row.get(key) != value:
					row.set(key, value)
					changed = True
			continue
		settings.append("invoice_fields", field)
		changed = True

	if changed:
		settings.flags.ignore_permissions = True
		settings.save()
