frappe.provide("retail_shop");

// The "like" (heart) feature is not used by this single-shop POS workflow
// and is disabled everywhere, not just hidden on specific list routes (see
// retail_shop.bundle.css for the matching visual hide). No-op the toggle so
// a stray heart that shows up in some view we haven't styled yet still can't
// actually record a like.
frappe.ui.toggle_like = function () {};

retail_shop.visible_workspaces = ["KBM Lighting Trading"];
retail_shop.home_workspace = "KBM Lighting Trading";
retail_shop.section_meta = {
	"Sales Counter": {
		slug: "sales-counter",
		kicker: "Counter",
		description: "Fast actions for checkout, invoicing, and stock lookup.",
		primary: true,
	},
	"Back Office": {
		slug: "back-office",
		kicker: "Operations",
		description: "Stock in, stock count, and commission settlement.",
	},
	"Reports & Audit": {
		slug: "reports-audit",
		kicker: "Control",
		description: "Financial visibility, stock value, and audit follow-up.",
	},
	"Catalog & Contacts": {
		slug: "catalog-contacts",
		kicker: "Directory",
		description: "Products, categories, electricians, customers, and suppliers.",
	},
	"Staff Management": {
		slug: "staff-management",
		kicker: "Team",
		description: "Manage store staff accounts and desk access.",
		primary: true,
	},
	"Store Configuration": {
		slug: "store-configuration",
		kicker: "Settings",
		description: "Commission rules, store defaults, and accepted payment modes.",
		primary: true,
	},
};
retail_shop.link_meta = {
	"New Sale": "Open the cashier and start a sale.",
	"Sales History": "Review completed counter sales.",
	"Credit Sales": "Create or review customer credit sales.",
	"Stock Balance": "Check current availability before selling.",
	"Stock In": "Record supplier purchases and add stock.",
	"Stock Count": "Correct counted stock differences.",
	"Commission Payment": "Settle electrician commissions.",
	"Sales Report": "Track sales volume and momentum.",
	"Profit Report": "See margin performance by transaction.",
	"Inventory Valuation": "Measure current stock value.",
	"Customer Balance Report": "Review unpaid customer balances.",
	"Supplier Balance Report": "Check outstanding supplier balances.",
	"Purchase Report": "Monitor purchasing activity and trends.",
	"Electrician Commission Report": "Audit electrician earnings.",
	"Retail Audit Log": "Inspect sensitive retail changes.",
	"Products": "Manage sellable products and prices.",
	"Categories": "Group products such as bulbs, switches, and cable.",
	"Electrician": "Maintain electrician records and rates.",
	"Customer": "Create and update customer profiles.",
	"Supplier": "Maintain supplier information.",
	"Users": "Add store logins with a username, role, and password.",
	"Retail Shop Settings": "Configure default store behavior.",
	"Retail Commission Settings": "Set commission rates and rules.",
	"Mode of Payment": "Manage accepted payment methods.",
};


retail_shop.get_user_roles = function () {
	return frappe.boot?.user?.roles || [];
};

retail_shop.has_any_role = function (roles) {
	const user_roles = new Set(retail_shop.get_user_roles());
	return roles.some((role) => user_roles.has(role));
};

// The desk navbar's Help dropdown (docs, forum, "Report an Issue", "About",
// etc.) has no per-role visibility setting in core Frappe, and is entirely
// Frappe-framework/developer-facing content — neither retail role has any
// use for it, same as the rest of the technical-admin-only surface (see
// modules.COMMON_BLOCKED_MODULES). Hide it for anyone without System Manager.
//
// A plain "hide" class isn't enough: the <li> already carries Bootstrap's
// own d-none/d-lg-block responsive classes (display:none/block !important),
// and .d-lg-block's rule is declared later in the compiled stylesheet than
// Frappe's .hide rule — same specificity, both !important, so cascade order
// lets .d-lg-block win at desktop widths. Setting the inline style directly
// with !important priority always beats a stylesheet rule, important or not.
retail_shop.hide_help_dropdown_for_non_technical_users = function () {
	if (retail_shop.has_any_role(["Administrator", "System Manager", "Technical Admin"])) {
		return;
	}
	document.querySelectorAll(".dropdown-help").forEach((el) => {
		el.style.setProperty("display", "none", "important");
	});
};

retail_shop.should_filter_home_workspace = function () {
	return retail_shop.has_any_role([
		"Shop Admin",
		"Salesperson",
		"Technical Admin",
		"System Manager",
		"Administrator",
	]);
};

retail_shop.is_retail_admin = function () {
	return retail_shop.has_any_role(["Shop Admin"]);
};

retail_shop.get_visible_workspaces = function () {
	const visible = [...retail_shop.visible_workspaces];
	if (
		retail_shop.has_any_role([
			"Shop Admin",
			"Technical Admin",
			"System Manager",
			"Administrator",
		])
	) {
		visible.push("Staff");
		visible.push("Store Settings");
	}
	return visible;
};

retail_shop.is_retail_workspace = function (page) {
	const workspace_name = page?.name || page?.title || page || "";
	return retail_shop.get_visible_workspaces().some(
		(visible_workspace) => frappe.router?.slug(workspace_name) === frappe.router?.slug(visible_workspace)
	);
};

retail_shop.filter_workspace_pages = function (pages) {
	return (pages || []).filter((page) => retail_shop.is_retail_workspace(page));
};

retail_shop.filter_boot_workspaces = function (pages) {
	return retail_shop.filter_workspace_pages(pages).filter((page) => (page?.name || page?.title) !== "Home");
};

retail_shop.is_visible_workspace_slug = function (slug) {
	return retail_shop.get_visible_workspaces().some(
		(workspace) => frappe.router?.slug(workspace) === slug
	);
};

retail_shop.clear_stale_workspace_state = function () {
	if (!retail_shop.should_filter_home_workspace()) {
		return;
	}

	const current_page = localStorage.getItem("current_page");
	if (current_page && !retail_shop.get_visible_workspaces().includes(current_page)) {
		localStorage.removeItem("current_page");
		localStorage.removeItem("is_current_page_public");
	}

	const saved_route = localStorage.getItem("session_last_route");
	const match = saved_route?.match(/^\/app\/([^/?#]+)$/);
	if (match && !retail_shop.is_visible_workspace_slug(match[1]) && match[1] !== "home") {
		localStorage.removeItem("session_last_route");
	}
};

retail_shop.get_workspace_context = function () {
	const route = frappe.get_route() || [];
	const path_parts = window.location.pathname.replace(/\/+$/, "").split("/");
	const path_slug = path_parts[path_parts.length - 1] || "";
	const workspace_name = route[1] === "private" ? route[2] : route[1];
	const route_slug = workspace_name ? frappe.router?.slug(workspace_name) : "";
	const visible_slugs = retail_shop.get_visible_workspaces().map((workspace) =>
		frappe.router?.slug(workspace)
	);
	const home_slug = frappe.router?.slug(retail_shop.home_workspace);
	const fallback_slug = visible_slugs.includes(path_slug) ? path_slug : "";
	const active_slug = route[0] === "Workspaces" && route_slug ? route_slug : fallback_slug;
	const is_workspace_route = route[0] === "Workspaces" || Boolean(fallback_slug);

	return {
		active_slug,
		home_slug,
		is_workspace_route,
		is_home_route: is_workspace_route && active_slug === home_slug,
	};
};

retail_shop.looks_like_retail_workspace = function () {
	const titles = Array.from(document.querySelectorAll(".layout-main-section .widget-title"))
		.map((node) => node.textContent?.trim())
		.filter(Boolean);

	const matched = Object.keys(retail_shop.section_meta).filter((title) => titles.includes(title));
	return matched.length >= 2;
};

retail_shop.is_retail_shop_path = function () {
	const path = window.location.pathname.replace(/\/+$/, "");
	if (path === "/app/home") {
		return true;
	}

	const slug = path.replace(/^\/app\//, "");
	return retail_shop.get_visible_workspaces().some(
		(workspace) => frappe.router?.slug(workspace) === slug
	);
};

retail_shop.is_retail_workspace_surface = function () {
	const context = retail_shop.get_workspace_context();
	return (
		context.is_home_route ||
		retail_shop.is_retail_shop_path() ||
		retail_shop.looks_like_retail_workspace()
	);
};

retail_shop.sync_workspace_page_state = function () {
	const context = retail_shop.get_workspace_context();
	const is_retail_route = retail_shop.is_retail_workspace_surface();
	const allow_workspace_filtering = retail_shop.should_filter_home_workspace();

	document.body.classList.toggle(
		"retail-shop-workspace-active",
		context.is_workspace_route && allow_workspace_filtering
	);
	document.body.classList.toggle("retail-shop-home-active", is_retail_route);
	retail_shop.decorate_retail_workspace();
};

retail_shop.patch_home_route = function () {
	if (!retail_shop.should_filter_home_workspace()) {
		return;
	}

	const home_slug = frappe.router?.slug(retail_shop.home_workspace);
	if (!home_slug) {
		return;
	}

	frappe.re_route = frappe.re_route || {};
	frappe.re_route.home = home_slug;

	const current_url = new URL(window.location.href);
	if (current_url.pathname === "/app" || current_url.pathname === "/app/home") {
		current_url.pathname = `/app/${home_slug}`;
		window.history.replaceState({}, "", current_url.toString());
	}
};

retail_shop.get_native_card_title = function (widget) {
	return (
		widget.querySelector(".widget-title .ellipsis")?.textContent?.trim() ||
		widget.querySelector(".widget-title")?.textContent?.trim() ||
		""
	);
};

retail_shop.decorate_card_header = function (widget, head, meta) {
	head.querySelector(".retail-shop-card-kicker-row")?.remove();
	const kicker_row = document.createElement("div");
	const kicker = document.createElement("span");
	const count = document.createElement("span");

	kicker_row.className = "retail-shop-card-kicker-row";
	kicker.className = "retail-shop-card-kicker";
	count.className = "retail-shop-card-count";
	kicker.textContent = meta.kicker || "Section";
	count.textContent = String(widget.querySelectorAll(".link-item").length);

	kicker_row.appendChild(kicker);
	kicker_row.appendChild(count);
	head.prepend(kicker_row);
};

retail_shop.decorate_link_tile = function (link, meta, is_primary) {
	link.classList.add("retail-shop-link-tile");
	if (is_primary) {
		link.classList.add("retail-shop-link-tile--primary");
	}

	const link_text = link.querySelector(".link-text");
	const link_content = link.querySelector(".link-content");
	if (!link_text || !link_content) {
		return;
	}

	let copy = link.querySelector(".retail-shop-link-copy");
	if (!copy) {
		copy = document.createElement("span");
		copy.className = "retail-shop-link-copy";
		link_text.replaceWith(copy);
		copy.appendChild(link_text);
	}

	link_text.classList.add("retail-shop-link-title");

	let description = link.querySelector(".retail-shop-link-description");
	if (meta?.description) {
		if (!description) {
			description = document.createElement("span");
			description.className = "retail-shop-link-description";
			copy.appendChild(description);
		}
		description.textContent = meta.description;
	} else {
		description?.remove();
	}
};

retail_shop.set_active_workspace_tab = function (shell, section_slug) {
	if (!shell) {
		return;
	}

	shell.dataset.activeSection = section_slug;
	shell.querySelectorAll(".retail-shop-tab").forEach((tab) => {
		tab.classList.toggle("is-active", tab.dataset.section === section_slug);
		tab.setAttribute("aria-selected", tab.dataset.section === section_slug ? "true" : "false");
	});
	shell.querySelectorAll(".retail-shop-tab-panel").forEach((panel) => {
		panel.classList.toggle("is-active", panel.dataset.section === section_slug);
	});
};

retail_shop.build_tabbed_workspace = function () {
	const redactor = document.querySelector(".layout-main-section .codex-editor__redactor");
	if (!redactor) {
		return;
	}

	const card_blocks = Array.from(redactor.querySelectorAll(".ce-block")).filter((block) =>
		block.querySelector(".widget.links-widget-box.retail-shop-card[data-retail-section]")
	);
	if (card_blocks.length < 2) {
		return;
	}

	let shell = redactor.querySelector(".retail-shop-tabs-shell");
	if (!shell) {
		shell = document.createElement("section");
		shell.className = "retail-shop-tabs-shell";
		shell.innerHTML = `
			<div class="retail-shop-tabs" role="tablist" aria-label="Retail sections"></div>
			<div class="retail-shop-tab-panels"></div>
		`;
		redactor.insertBefore(shell, card_blocks[0]);
	}

	const tabs = shell.querySelector(".retail-shop-tabs");
	const panels = shell.querySelector(".retail-shop-tab-panels");
	const active_section = shell.dataset.activeSection;

	tabs.innerHTML = "";

	card_blocks.forEach((block, index) => {
		const card = block.querySelector(".widget.links-widget-box.retail-shop-card[data-retail-section]");
		const title = retail_shop.get_native_card_title(card);
		const meta = retail_shop.section_meta[title] || {};
		const section_slug = card.dataset.retailSection || meta.slug || frappe.router.slug(title || `section-${index}`);
		const tab = document.createElement("button");

		if (block.parentElement !== panels) {
			panels.appendChild(block);
		}

		block.classList.add("retail-shop-tab-panel");
		block.dataset.section = section_slug;

		tab.type = "button";
		tab.className = "retail-shop-tab";
		tab.dataset.section = section_slug;
		tab.setAttribute("role", "tab");
		tab.innerHTML = `<span class="retail-shop-tab-title">${title}</span>`;
		tab.addEventListener("click", () => retail_shop.set_active_workspace_tab(shell, section_slug));
		tabs.appendChild(tab);
	});

	retail_shop.set_active_workspace_tab(
		shell,
		active_section && panels.querySelector(`.retail-shop-tab-panel[data-section="${active_section}"]`)
			? active_section
			: card_blocks[0].dataset.section || card_blocks[0].querySelector(".widget.links-widget-box")?.dataset.retailSection
	);
};

retail_shop.decorate_native_workspace_cards = function (is_retail_home) {
	const widgets = document.querySelectorAll(".layout-main-section .widget.links-widget-box");

	widgets.forEach((widget) => {
		const title = retail_shop.get_native_card_title(widget);
		const meta = retail_shop.section_meta[title];
		const body = widget.querySelector(".widget-body");
		const head = widget.querySelector(".widget-head");

		widget.classList.remove(
			"retail-shop-card",
			"retail-shop-card--primary",
			"retail-shop-card--secondary",
			"retail-shop-card--sales-counter",
			"retail-shop-card--back-office",
			"retail-shop-card--reports-audit",
			"retail-shop-card--catalog-contacts"
		);
		widget.removeAttribute("data-retail-section");
		body?.classList.remove("retail-shop-card-body");

		widget.querySelectorAll(".link-item").forEach((link) => {
			link.classList.remove("retail-shop-link-tile", "retail-shop-link-tile--primary");
		});

		widget.querySelector(".retail-shop-card-description")?.remove();
		widget.querySelector(".retail-shop-card-kicker-row")?.remove();

		if (!is_retail_home || !meta) {
			return;
		}

		widget.classList.add("retail-shop-card");
		widget.classList.add(meta.primary ? "retail-shop-card--primary" : "retail-shop-card--secondary");
		widget.classList.add(`retail-shop-card--${meta.slug}`);
		widget.dataset.retailSection = meta.slug;
		body?.classList.add("retail-shop-card-body");

		if (head) {
			retail_shop.decorate_card_header(widget, head, meta);
			if (meta.description) {
				const note = document.createElement("div");
				note.className = "retail-shop-card-description";
				note.textContent = meta.description;
				head.appendChild(note);
			}
		}

		widget.querySelectorAll(".link-item").forEach((link) => {
			const label = link.querySelector(".link-text")?.textContent?.trim() || "";
			const link_meta = retail_shop.link_meta[label];
			retail_shop.decorate_link_tile(
				link,
				typeof link_meta === "string" ? { description: link_meta } : link_meta,
				meta.primary
			);
		});
	});
};

retail_shop.patch_boot_workspaces = function () {
	if (retail_shop.boot_workspaces_patched) {
		return;
	}

	if (!Array.isArray(frappe.boot?.allowed_workspaces) || !frappe.boot?.user?.roles) {
		setTimeout(retail_shop.patch_boot_workspaces, 50);
		return;
	}

	if (retail_shop.should_filter_home_workspace()) {
		frappe.boot.allowed_workspaces = retail_shop.filter_boot_workspaces(
			frappe.boot.allowed_workspaces
		);
	}
	retail_shop.boot_workspaces_patched = true;
};

retail_shop.restrict_workspace_payload = function (data) {
	if (!data || !retail_shop.should_filter_home_workspace()) {
		return data;
	}
	if (data.pages) {
		data.pages = retail_shop.filter_workspace_pages(data.pages);
	}
	data.has_access = 0;
	data.has_create_access = 0;
	return data;
};

retail_shop.patch_sidebar_xcall = function () {
	if (retail_shop.sidebar_xcall_patched) {
		return;
	}
	if (typeof frappe?.xcall !== "function") {
		setTimeout(retail_shop.patch_sidebar_xcall, 20);
		return;
	}

	const original_xcall = frappe.xcall;
	frappe.xcall = function (method, params) {
		const result = original_xcall.apply(this, arguments);
		if (method !== "frappe.desk.desktop.get_workspace_sidebar_items") {
			return result;
		}
		return Promise.resolve(result).then((data) => retail_shop.restrict_workspace_payload(data));
	};
	retail_shop.sidebar_xcall_patched = true;
};

retail_shop.hide_extra_sidebar_items = function () {
	if (!retail_shop.should_filter_home_workspace()) {
		return;
	}

	const allowed = new Set(
		retail_shop.get_visible_workspaces().map((name) => (name || "").trim().toLowerCase())
	);
	document.querySelectorAll(".desk-sidebar .sidebar-item-container").forEach((el) => {
		const name = (el.getAttribute("item-name") || "").trim().toLowerCase();
		if (name && !allowed.has(name)) {
			el.style.setProperty("display", "none", "important");
		}
	});
};

retail_shop.patch_workspace_sidebar = function () {
	if (retail_shop.workspace_sidebar_patched) {
		return;
	}

	if (!frappe.views?.Workspace) {
		setTimeout(retail_shop.patch_workspace_sidebar, 30);
		return;
	}

	const original_get_pages = frappe.views.Workspace.prototype.get_pages;

	frappe.views.Workspace.prototype.get_pages = function () {
		return Promise.resolve(original_get_pages.call(this)).then((data) =>
			retail_shop.restrict_workspace_payload(data)
		);
	};

	retail_shop.clear_stale_workspace_state();
	retail_shop.workspace_sidebar_patched = true;
};

retail_shop.patch_workspace_show_page = function () {
	if (retail_shop.workspace_show_page_patched) {
		return;
	}

	if (!frappe.views?.Workspace) {
		setTimeout(retail_shop.patch_workspace_show_page, 30);
		return;
	}

	const original_show_page = frappe.views.Workspace.prototype.show_page;

	frappe.views.Workspace.prototype.show_page = async function (...args) {
		const result = await original_show_page.apply(this, args);
		window.requestAnimationFrame(() => retail_shop.sync_workspace_page_state());
		window.setTimeout(() => retail_shop.sync_workspace_page_state(), 80);
		return result;
	};

	retail_shop.workspace_show_page_patched = true;
};

retail_shop.decorate_retail_workspace = function () {
	if (retail_shop.decorating_workspace) {
		return;
	}

	retail_shop.decorating_workspace = true;
	// decorate_native_workspace_cards / build_tabbed_workspace
	// always tear down and rebuild markup, even when nothing conceptually changed.
	// Without pausing the observer, every one of those writes would be picked up by
	// observe_workspace_widgets' MutationObserver and re-trigger this function forever.
	retail_shop.workspace_widget_observer?.disconnect();

	try {
		retail_shop.hide_extra_sidebar_items();
		const is_retail_home =
			document.body.classList.contains("retail-shop-home-active") ||
			retail_shop.is_retail_workspace_surface();
		retail_shop.decorate_native_workspace_cards(is_retail_home);

		if (!is_retail_home) {
			return;
		}

		retail_shop.build_tabbed_workspace();
	} finally {
		retail_shop.decorating_workspace = false;
		retail_shop.workspace_widget_observer?.observe(document.body, {
			childList: true,
			subtree: true,
		});
	}
};

retail_shop.schedule_workspace_decoration = function () {
	if (retail_shop.workspace_decoration_scheduled) {
		return;
	}

	retail_shop.workspace_decoration_scheduled = true;
	window.requestAnimationFrame(() => {
		retail_shop.workspace_decoration_scheduled = false;
		retail_shop.decorate_retail_workspace();
	});
};

retail_shop.observe_workspace_widgets = function () {
	if (retail_shop.workspace_widget_observer) {
		return;
	}

	retail_shop.workspace_widget_observer = new MutationObserver(() => {
		retail_shop.schedule_workspace_decoration();
	});

	retail_shop.workspace_widget_observer.observe(document.body, {
		childList: true,
		subtree: true,
	});
};

retail_shop.init_workspace_customizations = function () {
	retail_shop.clear_stale_workspace_state();
	retail_shop.patch_home_route();
	retail_shop.patch_sidebar_xcall();
	retail_shop.patch_boot_workspaces();
	retail_shop.patch_workspace_sidebar();
	retail_shop.patch_workspace_show_page();
	retail_shop.observe_workspace_widgets();
	retail_shop.hide_extra_sidebar_items();
	retail_shop.sync_workspace_page_state();
	frappe.after_ajax?.(() => {
		retail_shop.hide_extra_sidebar_items();
		retail_shop.sync_workspace_page_state();
	});
};

retail_shop.patch_logout_redirect = function () {
	if (!retail_shop.should_filter_home_workspace() || !frappe.app) {
		return;
	}

	frappe.app.redirect_to_login = function () {
		const target = window.location.pathname + window.location.search;
		window.location.href = `/retail-login?redirect_to=${encodeURIComponent(target)}`;
	};
};

// Frappe restores `session_last_route` before it computes the default
// workspace. Clear the known stale ERPNext workspace state eagerly so
// retail users can fall through to their own home workspace route.
if (localStorage.getItem("session_last_route") === "/app/erpnext-settings") {
	localStorage.removeItem("session_last_route");
}

if (localStorage.getItem("current_page") === "ERPNext Settings") {
	localStorage.removeItem("current_page");
	localStorage.removeItem("is_current_page_public");
}

retail_shop.patch_sidebar_xcall();
retail_shop.patch_workspace_sidebar();

// The navbar is rendered once during desk boot, before any route/ready
// event we could otherwise hook into — a MutationObserver catches it
// reliably regardless of script load-order timing.
if ($(".dropdown-help").length) {
	retail_shop.hide_help_dropdown_for_non_technical_users();
} else {
	const observer = new MutationObserver(() => {
		if ($(".dropdown-help").length) {
			retail_shop.hide_help_dropdown_for_non_technical_users();
			observer.disconnect();
		}
	});
	observer.observe(document.body, { childList: true, subtree: true });
}

frappe.router?.on?.("change", retail_shop.sync_workspace_page_state);

if (document.readyState === "loading") {
	document.addEventListener("DOMContentLoaded", () => retail_shop.init_workspace_customizations(), {
		once: true,
	});
} else {
	window.setTimeout(() => retail_shop.init_workspace_customizations(), 0);
}

window.setTimeout(() => retail_shop.patch_logout_redirect(), 0);
