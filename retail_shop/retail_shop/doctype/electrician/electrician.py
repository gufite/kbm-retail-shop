import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

from retail_shop.utils.commission import validate_commission_rate_fields


class Electrician(Document):
	def autoname(self):
		candidate = (self.electrician_name or "").strip()
		if candidate and not frappe.db.exists("Electrician", candidate):
			self.name = candidate
		else:
			self.name = make_autoname("ELEC-.#####")

	def validate(self):
		validate_commission_rate_fields(self, type_required=False)

