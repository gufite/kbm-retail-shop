frappe.ui.form.on("Purchase Entry Item", {
	item_code(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.item_code) {
			return;
		}

		frappe.db
			.get_value("Item", row.item_code, [
				"item_name",
				"standard_rate",
				"custom_purchase_unit_price",
				"custom_minimum_selling_price",
			])
			.then((r) => {
			const product = r && r.message;
			if (!product || !product.item_name) {
				return;
			}

			frappe.model.set_value(cdt, cdn, "item_name", product.item_name);
			if (!row.selling_unit_price && product.standard_rate) {
				frappe.model.set_value(cdt, cdn, "selling_unit_price", product.standard_rate);
			}
			if (!row.unit_purchase_price && product.custom_purchase_unit_price) {
				frappe.model.set_value(cdt, cdn, "unit_purchase_price", product.custom_purchase_unit_price);
			}
			if (!row.minimum_selling_price) {
				frappe.model.set_value(
					cdt,
					cdn,
					"minimum_selling_price",
					product.custom_minimum_selling_price || product.standard_rate
				);
			}
			frappe.show_alert({
				message: __(
					"This product already exists. Quantity will be added to current stock, and the description will stay as {0}.",
					[product.item_name]
				),
				indicator: "blue",
			});
		});
	},
});
