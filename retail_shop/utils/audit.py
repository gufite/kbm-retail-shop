import frappe
from frappe.utils import now_datetime


def log_audit_event(event_type: str, reference_doctype: str = None, reference_name: str = None, details: str = None):
	frappe.get_doc(
		{
			"doctype": "Retail Audit Log",
			"event_type": event_type,
			"performed_by": frappe.session.user,
			"performed_on": now_datetime(),
			"reference_doctype": reference_doctype,
			"reference_name": reference_name,
			"details": details,
		}
	).insert(ignore_permissions=True)


def log_field_changes(doc, fields: list[str], event_type: str, label_map: dict[str, str] = None):
	before = doc.get_doc_before_save()
	if not before:
		return

	label_map = label_map or {}
	changes = []
	for fieldname in fields:
		old_value = before.get(fieldname)
		new_value = doc.get(fieldname)
		if old_value != new_value:
			label = label_map.get(fieldname, fieldname)
			changes.append(f"{label}: {old_value} -> {new_value}")

	if changes:
		log_audit_event(
			event_type=event_type,
			reference_doctype=doc.doctype,
			reference_name=doc.name,
			details="; ".join(changes),
		)


def log_commission_settings_change(doc, method=None):
	log_field_changes(
		doc,
		["commission_type", "commission_percentage", "fixed_commission_amount"],
		event_type="Commission Setting Changed",
	)


def log_electrician_commission_change(doc, method=None):
	log_field_changes(
		doc,
		["commission_type", "commission_percentage", "fixed_commission_amount"],
		event_type="Commission Setting Changed",
		label_map={
			"commission_type": "Commission Override Type",
			"commission_percentage": "Commission Percentage",
			"fixed_commission_amount": "Fixed Commission Amount",
		},
	)


def log_user_role_change(doc, method=None):
	before = doc.get_doc_before_save()
	if not before:
		return

	old_roles = {row.role for row in (before.get("roles") or [])}
	new_roles = {row.role for row in (doc.get("roles") or [])}
	if old_roles == new_roles:
		return

	added = new_roles - old_roles
	removed = old_roles - new_roles
	details = []
	if added:
		details.append(f"Added roles: {', '.join(sorted(added))}")
	if removed:
		details.append(f"Removed roles: {', '.join(sorted(removed))}")

	log_audit_event(
		event_type="User Management Change",
		reference_doctype=doc.doctype,
		reference_name=doc.name,
		details="; ".join(details),
	)
