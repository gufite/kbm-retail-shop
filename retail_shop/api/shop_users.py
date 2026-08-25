import re

import frappe
from frappe import _
from frappe.utils import cint, validate_email_address

from retail_shop.setup.defaults import (
	SALESPERSON_ROLE,
	SHOP_ADMIN_ROLE,
	TECHNICAL_ADMIN_ROLE,
	is_technical_admin,
)

SHOP_ROLES = (TECHNICAL_ADMIN_ROLE, SHOP_ADMIN_ROLE, SALESPERSON_ROLE)
EMAIL_DOMAIN = "kbmlight.local"
_USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")
_RESERVED_USERNAMES = {"administrator", "guest"}


def _caller_roles():
	return set(frappe.get_roles())


def _ensure_can_manage_users():
	roles = _caller_roles()
	if is_technical_admin(roles) or SHOP_ADMIN_ROLE in roles:
		return
	frappe.throw(_("Not permitted"), frappe.PermissionError)


def _allowed_roles_for_caller():
	if is_technical_admin(_caller_roles()):
		return list(SHOP_ROLES)
	return [SALESPERSON_ROLE]


def _shop_role_of(user: str) -> str | None:
	roles = set(frappe.get_roles(user))
	for role in SHOP_ROLES:
		if role in roles:
			return role
	return None


def _is_protected_account(user: str) -> bool:
	return user in ("Administrator", "Guest")


def _email_for_username(username: str) -> str:
	return f"{username}@{EMAIL_DOMAIN}"


def _ensure_can_edit(user: str):
	if user == "Guest":
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	if _is_protected_account(user):
		if not is_technical_admin():
			frappe.throw(_("Not permitted"), frappe.PermissionError)
		return

	role = _shop_role_of(user)
	if role not in _allowed_roles_for_caller():
		frappe.throw(_("You can only manage shop users."), frappe.PermissionError)


@frappe.whitelist()
def list_shop_users():
	_ensure_can_manage_users()
	allowed = set(_allowed_roles_for_caller())

	users = frappe.get_all(
		"User",
		filters={"name": ["not in", ["Guest"]]},
		fields=["name", "full_name", "username", "email", "enabled", "last_login"],
		order_by="username asc, full_name asc",
	)
	rows = []
	for user in users:
		role = _shop_role_of(user.name)
		if role not in allowed:
			continue
		email = user.email or user.name
		generated_email = email.lower().endswith(f"@{EMAIL_DOMAIN}")
		rows.append(
			{
				"name": user.name,
				"username": user.username or user.name,
				"full_name": user.full_name,
				"email": None if generated_email else email,
				"role": role,
				"enabled": user.enabled,
				"last_login": user.last_login,
				"is_protected": _is_protected_account(user.name),
			}
		)
	return {"users": rows, "roles": _allowed_roles_for_caller()}


@frappe.whitelist()
def create_shop_user(
	username: str,
	password: str,
	role: str,
	full_name: str | None = None,
	email: str | None = None,
):
	_ensure_can_manage_users()

	username = (username or "").strip().lower()
	password = password or ""
	role = (role or "").strip()
	full_name = (full_name or "").strip() or username
	email = (email or "").strip().lower()

	if not username or not _USERNAME_RE.match(username):
		frappe.throw(_("Username can only contain letters, numbers, dot, dash, and underscore."))
	if username in _RESERVED_USERNAMES:
		frappe.throw(_("That username is reserved."))
	if len(password) < 6:
		frappe.throw(_("Password must be at least 6 characters."))
	if role not in _allowed_roles_for_caller():
		frappe.throw(_("You cannot assign the {0} role.").format(role), frappe.PermissionError)

	if email:
		validate_email_address(email, throw=True)
	else:
		email = _email_for_username(username)

	if frappe.db.exists("User", email) or frappe.db.exists("User", {"username": username}):
		frappe.throw(_("That username is already used."))

	doc = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": full_name,
			"username": username,
			"send_welcome_email": 0,
			"new_password": password,
			"user_type": "System User",
			"roles": [{"role": role}],
		}
	)
	doc.flags.ignore_password_policy = True
	doc.flags.no_welcome_mail = True
	doc.insert(ignore_permissions=True)
	return {"name": doc.name, "username": username, "role": role}


@frappe.whitelist()
def set_shop_user_enabled(user: str, enabled):
	_ensure_can_manage_users()
	_ensure_can_edit(user)
	if user == frappe.session.user and not cint(enabled):
		frappe.throw(_("You cannot disable your own account."))
	if _is_protected_account(user) and not cint(enabled):
		frappe.throw(_("The Administrator account cannot be disabled."))
	frappe.db.set_value("User", user, "enabled", cint(enabled))


@frappe.whitelist()
def set_shop_user_password(user: str, password: str):
	_ensure_can_manage_users()
	_ensure_can_edit(user)
	if len(password or "") < 6:
		frappe.throw(_("Password must be at least 6 characters."))
	doc = frappe.get_doc("User", user)
	doc.new_password = password
	doc.flags.ignore_password_policy = True
	doc.save(ignore_permissions=True)
