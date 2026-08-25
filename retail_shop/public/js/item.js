frappe.ui.form.on("Item", {
	refresh(frm) {
		frm.page.set_title(__("Product"));
	},
});

frappe.listview_settings["Item"] = {
	hide_name_column: true,
};
