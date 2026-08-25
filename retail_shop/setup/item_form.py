import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.utils import cstr


# Shop-facing Item form: Details tab only, with product/code/category/unit/prices.
HIDDEN_ITEM_TABS = (
	"dashboard_tab",
	"inventory_section",
	"variants_section",
	"accounting",
	"purchasing_tab",
	"quality_tab",
	"manufacturing",
	"sales_details",
	"item_tax_section_break",
)

HIDDEN_ITEM_FIELDS = (
	"naming_series",
	"allow_alternative_item",
	"is_stock_item",
	"has_variants",
	"opening_stock",
	"valuation_rate",
	"is_fixed_asset",
	"auto_create_assets",
	"is_grouped_asset",
	"asset_category",
	"asset_naming_series",
	"over_delivery_receipt_allowance",
	"over_billing_allowance",
	"brand",
	"unit_of_measure_conversion",
	"uoms",
	"sb_barcodes",
	"barcodes",
)

ITEM_LABELS = {
	"item_code": "Product Code",
	"item_name": "Product Name",
	"item_group": "Category",
	"stock_uom": "Unit",
	"standard_rate": "Selling Unit Price",
	"disabled": "Inactive",
}

HIDDEN_STOCK_COUNT_FIELDS = (
	"naming_series",
	"company",
	"purpose",
	"set_posting_time",
	"set_warehouse",
	"scan_barcode",
	"scan_mode",
	"last_scanned_warehouse",
	"expense_account",
	"difference_amount",
	"accounting_dimensions_section",
	"cost_center",
)

HIDDEN_STOCK_COUNT_ITEM_FIELDS = (
	"barcode",
	"has_item_scanned",
	"item_group",
	"warehouse",
	"stock_uom",
	"valuation_rate",
	"amount",
	"allow_zero_valuation_rate",
	"serial_no_and_batch_section",
	"add_serial_batch_bundle",
	"use_serial_batch_fields",
	"reconcile_all_serial_batch",
	"serial_and_batch_bundle",
	"current_serial_and_batch_bundle",
	"serial_no",
	"batch_no",
	"current_amount",
	"current_valuation_rate",
	"current_serial_no",
	"quantity_difference",
	"amount_difference",
)

STOCK_COUNT_LABELS = {
	"posting_date": "Count Date",
	"posting_time": "Count Time",
	"items": "Products",
	"custom_adjustment_reason": "Reason",
}

STOCK_COUNT_ITEM_LABELS = {
	"item_code": "Product Code",
	"item_name": "Product Name",
	"qty": "Counted Quantity",
	"current_qty": "System Quantity",
}


def ensure_item_form_tabs_hidden():
	ensure_shop_forms()


def ensure_shop_forms():
	_simplify_item_form()
	_simplify_stock_count_form()


def _simplify_item_form():
	for fieldname in HIDDEN_ITEM_TABS + HIDDEN_ITEM_FIELDS:
		_set_property("Item", fieldname, "hidden", "1", "Check")

	for fieldname, label in ITEM_LABELS.items():
		_set_property("Item", fieldname, "label", label, "Data")

	# Selling price is otherwise only shown while creating a new product.
	_set_property("Item", "standard_rate", "depends_on", "eval:true", "Data")
	_set_property("Item", "standard_rate", "hidden", "0", "Check")
	_set_property("Item", "standard_rate", "in_list_view", "1", "Check")


def _simplify_stock_count_form():
	for fieldname in HIDDEN_STOCK_COUNT_FIELDS:
		_set_property("Stock Reconciliation", fieldname, "hidden", "1", "Check")

	for fieldname, label in STOCK_COUNT_LABELS.items():
		_set_property("Stock Reconciliation", fieldname, "label", label, "Data")

	for fieldname in HIDDEN_STOCK_COUNT_ITEM_FIELDS:
		_set_property("Stock Reconciliation Item", fieldname, "hidden", "1", "Check")
		if fieldname in {"warehouse", "valuation_rate", "stock_uom", "barcode", "item_group"}:
			_set_property("Stock Reconciliation Item", fieldname, "in_list_view", "0", "Check")

	for fieldname, label in STOCK_COUNT_ITEM_LABELS.items():
		_set_property("Stock Reconciliation Item", fieldname, "label", label, "Data")

	_set_property("Stock Reconciliation Item", "current_qty", "in_list_view", "1", "Check")
	_set_property("Stock Reconciliation Item", "qty", "in_list_view", "1", "Check")
	_set_property("Stock Reconciliation", "company", "reqd", "0", "Check")
	_set_property("Stock Reconciliation", "purpose", "reqd", "0", "Check")
	_set_property("Stock Reconciliation Item", "warehouse", "reqd", "0", "Check")


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
