import frappe
from frappe import _

from retail_shop.setup.defaults import RETAIL_ADMIN_ROLE, RETAIL_SALESPERSON_ROLE

# Roles that make an account "technical" or another admin — never manageable
# through this narrow tool, even if they also happen to hold the Salesperson
# role. Keeps a Retail Administrator from touching System Manager accounts
# (or each other) through the back door of this API.
_PROTECTED_ROLES = {"System Manager", RETAIL_ADMIN_ROLE}


def _ensure_caller_is_retail_admin():
	if RETAIL_ADMIN_ROLE not in frappe.get_roles():
		frappe.throw(_("Not permitted"), frappe.PermissionError)


def _is_managed_salesperson(user: str) -> bool:
	if user in ("Administrator", "Guest"):
		return False

	roles = set(frappe.get_roles(user))
	if RETAIL_SALESPERSON_ROLE not in roles:
		return False

	return not roles.intersection(_PROTECTED_ROLES)


@frappe.whitelist()
def list_sales_staff():
	"""Every Salesperson-only account a Retail Administrator is allowed to manage."""
	_ensure_caller_is_retail_admin()

	users = frappe.get_all(
		"User",
		filters={"name": ["not in", ["Administrator", "Guest"]]},
		fields=["name", "full_name", "enabled", "last_login"],
		order_by="full_name asc",
	)
	return [user for user in users if _is_managed_salesperson(user.name)]


@frappe.whitelist()
def create_sales_staff(full_name: str, email: str):
	_ensure_caller_is_retail_admin()

	full_name = (full_name or "").strip()
	email = (email or "").strip().lower()
	if not full_name or not email:
		frappe.throw(_("Full Name and Email are required."))

	if frappe.db.exists("User", email):
		frappe.throw(_("A user with this email already exists."))

	first_name, _sep, last_name = full_name.partition(" ")

	doc = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": first_name,
			"last_name": last_name or None,
			"full_name": full_name,
			"user_type": "System User",
			"send_welcome_email": 1,
			"roles": [{"role": RETAIL_SALESPERSON_ROLE}],
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


@frappe.whitelist()
def set_sales_staff_enabled(user: str, enabled):
	_ensure_caller_is_retail_admin()

	if not _is_managed_salesperson(user):
		frappe.throw(_("You can only manage Salesperson accounts."), frappe.PermissionError)

	frappe.db.set_value("User", user, "enabled", frappe.utils.cint(enabled))


@frappe.whitelist()
def reset_sales_staff_password(user: str):
	_ensure_caller_is_retail_admin()

	if not _is_managed_salesperson(user):
		frappe.throw(_("You can only manage Salesperson accounts."), frappe.PermissionError)

	from frappe.core.doctype.user.user import reset_password

	reset_password(user)
