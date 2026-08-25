frappe.pages["shop-users"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Users"),
		single_column: true,
	});

	new ShopUsersPage(page);
};

class ShopUsersPage {
	constructor(page) {
		this.page = page;
		this.roles = [];
		this.page.set_primary_action(__("New User"), () => this.show_new_dialog(), "add");
		this.refresh();
	}

	refresh() {
		frappe.call({
			method: "retail_shop.api.shop_users.list_shop_users",
			callback: (r) => {
				const data = r.message || {};
				this.roles = data.roles || [];
				this.render(data.users || []);
			},
		});
	}

	render(rows) {
		const $wrapper = $(this.page.body).empty();

		if (!rows.length) {
			$wrapper.append(`<div class="text-muted padding">${__("No shop users yet.")}</div>`);
			return;
		}

		const $table = $(`
			<table class="table table-bordered">
				<thead>
					<tr>
						<th>${__("Username")}</th>
						<th>${__("Role")}</th>
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
			$tr.append(`<td>${frappe.utils.escape_html(row.username || row.name)}</td>`);
			$tr.append(`<td>${frappe.utils.escape_html(row.role || "")}</td>`);
			$tr.append(
				`<td><span class="indicator ${row.enabled ? "green" : "red"}">${
					row.enabled ? __("Active") : __("Disabled")
				}</span></td>`
			);
			$tr.append(`<td>${row.last_login ? comment_when(row.last_login) : __("Never")}</td>`);

			const $actions = $("<td></td>").appendTo($tr);
			if (!row.is_protected) {
				$(`<button class="btn btn-xs btn-secondary">${
					row.enabled ? __("Disable") : __("Enable")
				}</button>`)
					.on("click", () => this.toggle_enabled(row))
					.appendTo($actions);
				$actions.append(" ");
			}
			$(`<button class="btn btn-xs btn-default">${__("Set Password")}</button>`)
				.on("click", () => this.show_password_dialog(row))
				.appendTo($actions);
		});
	}

	show_new_dialog() {
		const dialog = new frappe.ui.Dialog({
			title: __("New User"),
			fields: [
				{ fieldname: "username", label: __("Username"), fieldtype: "Data", reqd: 1 },
				{
					fieldname: "role",
					label: __("Role"),
					fieldtype: "Select",
					options: this.roles.join("\n"),
					reqd: 1,
					default: this.roles[0],
				},
				{ fieldname: "password", label: __("Password"), fieldtype: "Password", reqd: 1 },
				{
					fieldname: "confirm_password",
					label: __("Confirm Password"),
					fieldtype: "Password",
					reqd: 1,
				},
			],
			primary_action_label: __("Create"),
			primary_action: (values) => {
				if (values.password !== values.confirm_password) {
					frappe.msgprint(__("Passwords do not match."));
					return;
				}
				frappe.call({
					method: "retail_shop.api.shop_users.create_shop_user",
					args: {
						username: values.username,
						password: values.password,
						role: values.role,
					},
					freeze: true,
					callback: () => {
						dialog.hide();
						frappe.show_alert({
							message: __("User created."),
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
			method: "retail_shop.api.shop_users.set_shop_user_enabled",
			args: { user: row.name, enabled: row.enabled ? 0 : 1 },
			freeze: true,
			callback: () => this.refresh(),
		});
	}

	show_password_dialog(row) {
		const dialog = new frappe.ui.Dialog({
			title: __("Set Password"),
			fields: [
				{
					fieldname: "password",
					label: __("New Password"),
					fieldtype: "Password",
					reqd: 1,
				},
			],
			primary_action_label: __("Save"),
			primary_action: (values) => {
				frappe.call({
					method: "retail_shop.api.shop_users.set_shop_user_password",
					args: { user: row.name, password: values.password },
					freeze: true,
					callback: () => {
						dialog.hide();
						frappe.show_alert({
							message: __("Password updated."),
							indicator: "green",
						});
					},
				});
			},
		});
		dialog.show();
	}
}
