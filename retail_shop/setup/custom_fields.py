from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def ensure_custom_fields():
	create_custom_fields(
		{
			"POS Invoice": _get_sales_custom_fields(insert_after="return_against"),
			"Sales Invoice": _get_sales_custom_fields(insert_after="return_against"),
			"Purchase Receipt": [
				{
					"fieldname": "custom_purchase_entry",
					"label": "Purchase Entry",
					"fieldtype": "Link",
					"options": "Purchase Entry",
					"insert_after": "return_against",
					"read_only": 1,
					"no_copy": 1,
				}
			],
			"Contact": [
				{
					"fieldname": "is_billing_contact",
					"label": "Is Billing Contact",
					"fieldtype": "Check",
					"insert_after": "is_primary_contact",
					"default": "0",
				}
			],
			"Stock Reconciliation": [
				{
					"fieldname": "custom_adjustment_reason",
					"label": "Reason",
					"fieldtype": "Small Text",
					"insert_after": "posting_date",
					"reqd": 1,
				}
			],
			"Item": [
				{
					"fieldname": "custom_purchase_unit_price",
					"label": "Purchase Unit Price",
					"fieldtype": "Currency",
					"insert_after": "standard_rate",
					"read_only": 1,
					"in_list_view": 1,
				}
			],
		},
		ignore_validate=True,
		update=True,
	)


def _get_sales_custom_fields(insert_after: str):
	fields = [
		{
			"fieldname": "custom_electrician",
			"label": "Electrician",
			"fieldtype": "Link",
			"options": "Electrician",
			"insert_after": insert_after,
		},
		{
			"fieldname": "custom_commission_type",
			"label": "Commission Type",
			"fieldtype": "Data",
			"insert_after": "custom_electrician",
			"read_only": 1,
			"no_copy": 1,
		},
		{
			"fieldname": "custom_commission_rate",
			"label": "Commission Rate",
			"fieldtype": "Float",
			"insert_after": "custom_commission_type",
			"read_only": 1,
			"no_copy": 1,
		},
		{
			"fieldname": "custom_commission_basis_amount",
			"label": "Commission Basis Amount",
			"fieldtype": "Currency",
			"insert_after": "custom_commission_rate",
			"read_only": 1,
			"no_copy": 1,
		},
		{
			"fieldname": "custom_commission_amount",
			"label": "Commission Amount",
			"fieldtype": "Currency",
			"insert_after": "custom_commission_basis_amount",
			"read_only": 1,
			"no_copy": 1,
		},
	]
	return fields
