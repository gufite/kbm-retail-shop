frappe.ui.form.on("Stock Reconciliation", {
	onload(frm) {
		if (!frm.is_new()) {
			return;
		}
		if (!frm.doc.purpose) {
			frm.set_value("purpose", "Stock Reconciliation");
		}
		frappe.db.get_value(
			"Retail Shop Settings",
			"Retail Shop Settings",
			["default_company", "default_warehouse"]
		).then((r) => {
			const settings = r && r.message;
			if (!settings) {
				return;
			}
			if (!frm.doc.company && settings.default_company) {
				frm.set_value("company", settings.default_company);
			}
			if (!frm.doc.set_warehouse && settings.default_warehouse) {
				frm.set_value("set_warehouse", settings.default_warehouse);
			}
		});
	},
	refresh(frm) {
		frm.page.set_title(__("Stock Count"));
	},
	items_add(frm, cdt, cdn) {
		if (frm.doc.set_warehouse) {
			frappe.model.set_value(cdt, cdn, "warehouse", frm.doc.set_warehouse);
		}
	},
});
