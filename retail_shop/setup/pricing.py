import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.utils import cstr


def ensure_sales_pricing_forms():
	for doctype in ("POS Invoice", "Sales Invoice"):
		_set_property(doctype, "apply_discount_on", "default", "Net Total", "Data")
		_set_property(doctype, "apply_discount_on", "hidden", "1", "Check")
		_set_property(doctype, "additional_discount_percentage", "hidden", "1", "Check")
		_set_property(doctype, "discount_amount", "hidden", "0", "Check")
		_set_property(doctype, "discount_amount", "label", "Transaction Discount", "Data")

	for doctype in ("POS Invoice Item", "Sales Invoice Item"):
		_set_property(doctype, "discount_percentage", "hidden", "1", "Check")
		_set_property(doctype, "discount_percentage", "in_list_view", "0", "Check")
		_set_property(doctype, "discount_amount", "hidden", "1", "Check")
		_set_property(doctype, "discount_amount", "in_list_view", "0", "Check")
		_set_property(doctype, "rate", "label", "Selling Price", "Data")
		_set_property(doctype, "rate", "read_only", "0", "Check")
		_set_property(doctype, "rate", "in_list_view", "1", "Check")


def _set_property(doctype, fieldname, property, value, property_type):
	if not frappe.get_meta(doctype).has_field(fieldname):
		return

	name = f"{doctype}-{fieldname}-{property}"
	if frappe.db.exists("Property Setter", name):
		if cstr(frappe.db.get_value("Property Setter", name, "value")) == cstr(value):
			return
		frappe.db.set_value("Property Setter", name, "value", value)
		return
	make_property_setter(
		doctype,
		fieldname,
		property,
		value,
		property_type,
		validate_fields_for_doctype=False,
	)
