from frappe.model.document import Document

from retail_shop.utils.commission import validate_commission_rate_fields


class RetailCommissionSettings(Document):
	def validate(self):
		validate_commission_rate_fields(self, type_required=True)

