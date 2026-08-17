import frappe
from frappe.model.document import Document


class RetailShopSettings(Document):
	def validate(self):
		if self.default_company and not self.default_currency:
			self.default_currency = frappe.db.get_value("Company", self.default_company, "default_currency")

