import frappe
from frappe.utils import flt


def update_product_prices(item_code, purchase_rate, selling_rate):
	"""Keep the product card's latest buy/sell prices in shop language fields."""
	purchase_rate = flt(purchase_rate)
	selling_rate = flt(selling_rate)
	values = {
		"last_purchase_rate": purchase_rate,
		"standard_rate": selling_rate,
	}
	if frappe.db.has_column("Item", "custom_purchase_unit_price"):
		values["custom_purchase_unit_price"] = purchase_rate
	frappe.db.set_value("Item", item_code, values, update_modified=False)
	_sync_selling_item_price(item_code, selling_rate)


def default_stock_uom() -> str:
	return frappe.db.get_single_value("Stock Settings", "stock_uom") or "Piece"


def _sync_selling_item_price(item_code, selling_rate):
	price_list = frappe.db.get_single_value("Selling Settings", "selling_price_list")
	if not price_list:
		price_list = frappe.db.get_value("Price List", {"selling": 1, "enabled": 1}, "name")
	if not price_list:
		return

	existing = frappe.db.get_value(
		"Item Price",
		{"item_code": item_code, "price_list": price_list},
		"name",
	)
	if existing:
		frappe.db.set_value("Item Price", existing, "price_list_rate", selling_rate, update_modified=False)
		return

	frappe.get_doc(
		{
			"doctype": "Item Price",
			"item_code": item_code,
			"price_list": price_list,
			"price_list_rate": selling_rate,
			"uom": frappe.db.get_value("Item", item_code, "stock_uom"),
			"currency": frappe.db.get_single_value("Retail Shop Settings", "default_currency"),
		}
	).insert(ignore_permissions=True)
