import frappe
from frappe import _

from retail_shop.api.shop_users import (
	create_shop_user,
	list_shop_users,
	set_shop_user_enabled,
	set_shop_user_password,
)
from retail_shop.setup.defaults import SALESPERSON_ROLE, SHOP_ADMIN_ROLE


def _ensure_caller_is_shop_admin():
	if SHOP_ADMIN_ROLE not in frappe.get_roles():
		frappe.throw(_("Not permitted"), frappe.PermissionError)


@frappe.whitelist()
def list_sales_staff():
	_ensure_caller_is_shop_admin()
	return list_shop_users()


@frappe.whitelist()
def create_sales_staff(username: str, password: str, full_name: str | None = None):
	_ensure_caller_is_shop_admin()
	return create_shop_user(username, password, SALESPERSON_ROLE, full_name)


@frappe.whitelist()
def set_sales_staff_enabled(user: str, enabled):
	_ensure_caller_is_shop_admin()
	return set_shop_user_enabled(user, enabled)


@frappe.whitelist()
def reset_sales_staff_password(user: str, password: str):
	_ensure_caller_is_shop_admin()
	return set_shop_user_password(user, password)
