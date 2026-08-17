frappe.pages["sales-staff"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Sales Staff"),
		single_column: true,
	});

	new SalesStaffPage(page);
};

class SalesStaffPage {
	constructor(page) {
		this.page = page;
		this.page.set_primary_action(__("New Salesperson"), () => this.show_new_dialog(), "add");
		this.refresh();
	}

	refresh() {
		frappe.call({
			method: "retail_shop.api.sales_staff.list_sales_staff",
			callback: (r) => this.render(r.message || []),
		});
	}

	render(rows) {
		const $wrapper = $(this.page.body).empty();

		if (!rows.length) {
			$wrapper.append(
				`<div class="text-muted padding">${__("No salesperson accounts yet.")}</div>`
			);
			return;
		}

		const $table = $(`
			<table class="table table-bordered">
				<thead>
					<tr>
						<th>${__("Name")}</th>
						<th>${__("Email")}</th>
						<th>${__("Status")}</th>
						<th>${__("Last Login")}</th>
						<th></th>
					</tr>
				</thead>
				<tbody></tbody>
			</table>
		`).appendTo($wrapper);
		const $tbody = $table.find("tbody");

		rows.forEach((row) => {
			const $tr = $("<tr></tr>").appendTo($tbody);
			$tr.append(`<td>${frappe.utils.escape_html(row.full_name || row.name)}</td>`);
			$tr.append(`<td>${frappe.utils.escape_html(row.name)}</td>`);
			$tr.append(
				`<td><span class="indicator ${row.enabled ? "green" : "red"}">${
					row.enabled ? __("Active") : __("Disabled")
				}</span></td>`
			);
			$tr.append(
				`<td>${row.last_login ? comment_when(row.last_login) : __("Never")}</td>`
			);

			const $actions = $("<td></td>").appendTo($tr);
			$(`<button class="btn btn-xs btn-secondary">${
				row.enabled ? __("Disable") : __("Enable")
			}</button>`)
				.on("click", () => this.toggle_enabled(row))
				.appendTo($actions);
			$actions.append(" ");
			$(`<button class="btn btn-xs btn-default">${__("Reset Password")}</button>`)
				.on("click", () => this.reset_password(row))
				.appendTo($actions);
		});
	}

	show_new_dialog() {
		const dialog = new frappe.ui.Dialog({
			title: __("New Salesperson"),
			fields: [
				{ fieldname: "full_name", label: __("Full Name"), fieldtype: "Data", reqd: 1 },
				{
					fieldname: "email",
					label: __("Email"),
					fieldtype: "Data",
					options: "Email",
					reqd: 1,
				},
			],
			primary_action_label: __("Create"),
			primary_action: (values) => {
				frappe.call({
					method: "retail_shop.api.sales_staff.create_sales_staff",
					args: values,
					freeze: true,
					callback: () => {
						dialog.hide();
						frappe.show_alert({
							message: __("Salesperson account created."),
							indicator: "green",
						});
						this.refresh();
					},
				});
			},
		});
		dialog.show();
	}

	toggle_enabled(row) {
		frappe.call({
			method: "retail_shop.api.sales_staff.set_sales_staff_enabled",
			args: { user: row.name, enabled: row.enabled ? 0 : 1 },
			freeze: true,
			callback: () => this.refresh(),
		});
	}

	reset_password(row) {
		frappe.confirm(__("Send a password reset email to {0}?", [row.name]), () => {
			frappe.call({
				method: "retail_shop.api.sales_staff.reset_sales_staff_password",
				args: { user: row.name },
				freeze: true,
			});
		});
	}
}
