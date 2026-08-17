import frappe
from frappe import _

from retail_shop.utils.audit import log_audit_event


def get_stock_alert_items():
	return frappe.db.sql(
		"""
		select
			bin_totals.item_code,
			bin_totals.qty,
			coalesce(nullif(item.safety_stock, 0), reorder_totals.max_reorder_level, 0) as threshold
		from (
			select item_code, sum(actual_qty) as qty
			from `tabBin`
			group by item_code
		) bin_totals
		inner join `tabItem` item on item.name = bin_totals.item_code
		left join (
			select parent, max(warehouse_reorder_level) as max_reorder_level
			from `tabItem Reorder`
			group by parent
		) reorder_totals on reorder_totals.parent = bin_totals.item_code
		""",
		as_dict=True,
	)


def get_stock_alert_counts():
	items = get_stock_alert_items()
	low_stock = [row for row in items if row.qty > 0 and row.threshold > 0 and row.qty <= row.threshold]
	out_of_stock = [row for row in items if row.qty <= 0]
	return {
		"low_stock_count": len(low_stock),
		"out_of_stock_count": len(out_of_stock),
		"low_stock_items": low_stock,
		"out_of_stock_items": out_of_stock,
	}


def notify_stock_alerts():
	alerts = get_stock_alert_counts()
	if not alerts["low_stock_items"] and not alerts["out_of_stock_items"]:
		return

	recipients = frappe.get_all(
		"Has Role", filters={"role": "Retail Administrator", "parenttype": "User"}, pluck="parent"
	)
	if not recipients:
		return

	subject = _("Stock alert: {0} low, {1} out of stock").format(
		len(alerts["low_stock_items"]), len(alerts["out_of_stock_items"])
	)
	item_lines = [f"{row.item_code}: {row.qty}" for row in (alerts["out_of_stock_items"] + alerts["low_stock_items"])]
	content = "<br>".join(item_lines)

	for user in recipients:
		frappe.get_doc(
			{
				"doctype": "Notification Log",
				"for_user": user,
				"type": "Alert",
				"subject": subject,
				"email_content": content,
			}
		).insert(ignore_permissions=True)


def require_adjustment_reason(doc, method=None):
	if not doc.get("custom_adjustment_reason"):
		frappe.throw(_("A reason is required for every inventory adjustment / stock count."))


def log_stock_adjustment(doc, method=None):
	log_audit_event(
		event_type="Inventory Adjustment",
		reference_doctype=doc.doctype,
		reference_name=doc.name,
		details=doc.get("custom_adjustment_reason"),
	)
