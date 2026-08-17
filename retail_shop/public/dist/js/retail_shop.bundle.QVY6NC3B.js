(()=>{frappe.provide("retail_shop");frappe.ui.toggle_like=function(){};retail_shop.visible_workspaces=["KBM Lighting Trading"];retail_shop.home_workspace="KBM Lighting Trading";retail_shop.primary_shortcuts=new Set(["Point of Sale","Counter Sales","Sales Invoice","Purchase Receipt","Stock Balance"]);retail_shop.section_meta={"Sales Counter":{slug:"sales-counter",kicker:"Counter",description:"Fast actions for checkout, invoicing, and stock lookup.",primary:!0},"Back Office":{slug:"back-office",kicker:"Operations",description:"Inventory adjustment, receiving, and commission settlement."},"Reports & Audit":{slug:"reports-audit",kicker:"Control",description:"Financial visibility, stock value, and audit follow-up."},"Catalog & Contacts":{slug:"catalog-contacts",kicker:"Directory",description:"Products, partners, electricians, and warehouse references."},"Staff Management":{slug:"staff-management",kicker:"Team",description:"Manage store staff accounts and desk access.",primary:!0},"Store Configuration":{slug:"store-configuration",kicker:"Settings",description:"Commission rules, store defaults, and accepted payment modes.",primary:!0}};retail_shop.link_meta={"Point of Sale":"Open the live cashier workspace.","Counter Sales":"Review or create counter sales slips.","Sales Invoice":"Handle standard billed sales.","Purchase Receipt":"Receive incoming supplier stock.","Stock Balance":"Check current availability before selling.","Purchase Entry":"Record supplier purchases in one place.","Stock Reconciliation":"Correct counted stock differences.","Commission Payment":"Settle electrician commissions.","Sales Report":"Track sales volume and momentum.","Profit Report":"See margin performance by transaction.","Inventory Valuation":"Measure current stock value.","Customer Balance Report":"Review unpaid customer balances.","Supplier Balance Report":"Check outstanding supplier balances.","Purchase Report":"Monitor purchasing activity and trends.","Electrician Commission Report":"Audit electrician earnings.","Retail Audit Log":"Inspect sensitive retail changes.",Item:"Manage sellable products and details.",Electrician:"Maintain electrician records and rates.",Customer:"Create and update customer profiles.",Supplier:"Maintain supplier information.",Warehouse:"Manage stock locations and stores.",User:"Manage staff accounts and login access.","Sales Staff":"Onboard, enable, disable, or reset passwords for salesperson accounts.","Retail Shop Settings":"Configure default store behavior.","Retail Commission Settings":"Set commission rates and rules.","Mode of Payment":"Manage accepted payment methods."};retail_shop.ensure_workspace_styles=function(){if(document.getElementById("retail-shop-workspace-styles"))return;let e=document.createElement("style");e.id="retail-shop-workspace-styles",e.textContent=`
		body.retail-shop-home-active .layout-main-section .editor-js-container {
			padding: 0 !important;
		}

		body.retail-shop-home-active .layout-main-section .widget.links-widget-box.retail-shop-card {
			height: 100%;
			padding: 0 !important;
			border: 0 !important;
			border-radius: 0 !important;
			background: transparent !important;
			box-shadow: none !important;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-tabs-shell {
			margin-bottom: 1.1rem;
			padding-bottom: 0.6rem;
			border-bottom: 1px solid rgba(111, 78, 55, 0.14);
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-tabs {
			display: flex;
			flex-wrap: wrap;
			gap: 0.4rem;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-tab {
			display: flex;
			align-items: center;
			gap: 0.5rem;
			padding: 0.45rem 0.85rem;
			border: 0;
			border-radius: 999px;
			background: transparent;
			color: #6e6255;
			font-size: 0.88rem;
			font-weight: 600;
			text-align: left;
			transition: background-color 0.18s ease, color 0.18s ease;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-tab:hover,
		body.retail-shop-home-active .layout-main-section .retail-shop-tab:focus-visible {
			background: rgba(111, 78, 55, 0.06);
			outline: none;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-tab.is-active {
			background: rgba(180, 138, 92, 0.16);
			color: #241d18;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-tab-title {
			line-height: 1.2;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-tab-panels {
			margin-top: 0;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-tab-panel {
			display: none !important;
			width: 100% !important;
			max-width: none !important;
			padding: 0 !important;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-tab-panel.is-active {
			display: block !important;
		}

		body.retail-shop-home-active .layout-main-section .widget.links-widget-box.retail-shop-card .widget-head {
			display: block !important;
			margin-bottom: 0.75rem !important;
			padding-bottom: 0.6rem !important;
			border-bottom: 1px solid rgba(111, 78, 55, 0.1) !important;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-card-kicker-row {
			display: flex;
			align-items: center;
			justify-content: space-between;
			gap: 0.75rem;
			margin-bottom: 0.55rem;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-card-kicker {
			display: inline-flex;
			align-items: center;
			padding: 0.22rem 0.55rem;
			border-radius: 999px;
			background: rgba(186, 151, 112, 0.12);
			color: #8a6844;
			font-size: 0.72rem;
			font-weight: 700;
			letter-spacing: 0.12em;
			text-transform: uppercase;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-card-count {
			display: inline-flex;
			align-items: center;
			justify-content: center;
			min-width: 2rem;
			height: 2rem;
			padding: 0 0.55rem;
			border-radius: 999px;
			background: rgba(41, 31, 23, 0.06);
			color: #57493d;
			font-size: 0.82rem;
			font-weight: 700;
		}

		body.retail-shop-home-active .layout-main-section .widget.links-widget-box.retail-shop-card .widget-title {
			font-size: 1.35rem !important;
			font-weight: 700 !important;
			letter-spacing: -0.03em !important;
			line-height: 1.1 !important;
		}

		body.retail-shop-home-active .layout-main-section .widget.links-widget-box.retail-shop-card--primary .widget-title {
			font-size: 1.55rem !important;
		}

		body.retail-shop-home-active .layout-main-section .widget.links-widget-box.retail-shop-card .card-description-btn {
			display: none !important;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-tab-panel .widget-title,
		body.retail-shop-home-active .layout-main-section .retail-shop-tab-panel .retail-shop-card-kicker-row {
			display: none !important;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-tab-panel .widget-head {
			margin-bottom: 0.6rem !important;
			padding-bottom: 0 !important;
			border-bottom: 0 !important;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-card-description {
			margin-top: 0.45rem;
			font-size: 0.89rem;
			line-height: 1.45;
			color: #6e675d;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-card-body {
			display: grid !important;
			grid-template-columns: repeat(auto-fill, minmax(9rem, 1fr)) !important;
			gap: 0.75rem !important;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-link-tile {
			display: flex !important;
			align-items: stretch !important;
			min-height: 4rem;
			margin: 0 !important;
			padding: 0 !important;
			border: 0 !important;
			border-radius: 0.85rem !important;
			background: #fffdf9 !important;
			box-shadow: none !important;
			text-decoration: none !important;
			overflow: hidden !important;
			transition: background-color 0.18s ease !important;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-link-tile:hover,
		body.retail-shop-home-active .layout-main-section .retail-shop-link-tile:focus-visible {
			background: #fdf9f2 !important;
			text-decoration: none !important;
			outline: none !important;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-link-tile .link-content {
			display: flex !important;
			align-items: flex-start !important;
			justify-content: space-between !important;
			width: 100% !important;
			padding: 0.95rem 1rem !important;
			gap: 0.75rem !important;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-link-copy {
			display: flex;
			flex-direction: column;
			align-items: flex-start;
			gap: 0.22rem;
			min-width: 0;
			flex: 1;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-link-tile .link-text,
		body.retail-shop-home-active .layout-main-section .retail-shop-link-title {
			font-size: 0.98rem !important;
			font-weight: 600 !important;
			line-height: 1.28 !important;
			white-space: normal !important;
			transition: font-weight 0.18s ease, color 0.18s ease !important;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-link-tile--primary .link-text,
		body.retail-shop-home-active .layout-main-section .retail-shop-link-tile--primary .retail-shop-link-title {
			font-size: 1.04rem !important;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-link-description {
			font-size: 0.78rem;
			line-height: 1.4;
			color: #7a6c5d;
			white-space: normal;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-link-tile:hover .link-text,
		body.retail-shop-home-active .layout-main-section .retail-shop-link-tile:focus-visible .link-text,
		body.retail-shop-home-active .layout-main-section .retail-shop-link-tile:hover .retail-shop-link-title,
		body.retail-shop-home-active .layout-main-section .retail-shop-link-tile:focus-visible .retail-shop-link-title {
			font-weight: 700 !important;
			color: #2d241b !important;
		}

		body.retail-shop-home-active .layout-main-section .retail-shop-link-tile .es-icon {
			display: none !important;
		}
	`,document.head.appendChild(e)};retail_shop.get_user_roles=function(){var e,o;return((o=(e=frappe.boot)==null?void 0:e.user)==null?void 0:o.roles)||[]};retail_shop.has_any_role=function(e){let o=new Set(retail_shop.get_user_roles());return e.some(t=>o.has(t))};retail_shop.hide_help_dropdown_for_non_technical_users=function(){retail_shop.has_any_role(["Administrator","System Manager"])||document.querySelectorAll(".dropdown-help").forEach(e=>{e.style.setProperty("display","none","important")})};retail_shop.should_filter_home_workspace=function(){return retail_shop.has_any_role(["Retail Administrator","Retail Salesperson"])};retail_shop.is_retail_admin=function(){return retail_shop.has_any_role(["Retail Administrator"])};retail_shop.get_visible_workspaces=function(){let e=[...retail_shop.visible_workspaces];return retail_shop.is_retail_admin()&&e.push("Store Settings"),e};retail_shop.is_retail_workspace=function(e){let o=(e==null?void 0:e.name)||(e==null?void 0:e.title)||e||"";return retail_shop.get_visible_workspaces().some(t=>{var a,r;return((a=frappe.router)==null?void 0:a.slug(o))===((r=frappe.router)==null?void 0:r.slug(t))})};retail_shop.filter_workspace_pages=function(e){return(e||[]).filter(o=>retail_shop.is_retail_workspace(o))};retail_shop.filter_boot_workspaces=function(e){return retail_shop.filter_workspace_pages(e).filter(o=>((o==null?void 0:o.name)||(o==null?void 0:o.title))!=="Home")};retail_shop.is_visible_workspace_slug=function(e){return retail_shop.get_visible_workspaces().some(o=>{var t;return((t=frappe.router)==null?void 0:t.slug(o))===e})};retail_shop.clear_stale_workspace_state=function(){if(!retail_shop.should_filter_home_workspace())return;let e=localStorage.getItem("current_page");e&&!retail_shop.get_visible_workspaces().includes(e)&&(localStorage.removeItem("current_page"),localStorage.removeItem("is_current_page_public"));let o=localStorage.getItem("session_last_route"),t=o==null?void 0:o.match(/^\/app\/([^/?#]+)$/);t&&!retail_shop.is_visible_workspace_slug(t[1])&&t[1]!=="home"&&localStorage.removeItem("session_last_route")};retail_shop.get_workspace_context=function(){var p,d;let e=frappe.get_route()||[],o=window.location.pathname.replace(/\/+$/,"").split("/"),t=o[o.length-1]||"",a=e[1]==="private"?e[2]:e[1],r=a?(p=frappe.router)==null?void 0:p.slug(a):"",i=retail_shop.get_visible_workspaces().map(_=>{var h;return(h=frappe.router)==null?void 0:h.slug(_)}),s=(d=frappe.router)==null?void 0:d.slug(retail_shop.home_workspace),n=i.includes(t)?t:"",c=e[0]==="Workspaces"&&r?r:n,l=e[0]==="Workspaces"||Boolean(n);return{active_slug:c,home_slug:s,is_workspace_route:l,is_home_route:l&&c===s}};retail_shop.looks_like_retail_workspace=function(){let e=Array.from(document.querySelectorAll(".layout-main-section .widget-title")).map(t=>{var a;return(a=t.textContent)==null?void 0:a.trim()}).filter(Boolean);return Object.keys(retail_shop.section_meta).filter(t=>e.includes(t)).length>=2};retail_shop.is_retail_shop_path=function(){let e=window.location.pathname.replace(/\/+$/,"");if(e==="/app/home")return!0;let o=e.replace(/^\/app\//,"");return retail_shop.get_visible_workspaces().some(t=>{var a;return((a=frappe.router)==null?void 0:a.slug(t))===o})};retail_shop.is_retail_workspace_surface=function(){return retail_shop.get_workspace_context().is_home_route||retail_shop.is_retail_shop_path()||retail_shop.looks_like_retail_workspace()};retail_shop.sync_workspace_page_state=function(){retail_shop.ensure_workspace_styles();let e=retail_shop.get_workspace_context(),o=retail_shop.is_retail_workspace_surface(),t=retail_shop.should_filter_home_workspace();document.body.classList.toggle("retail-shop-workspace-active",e.is_workspace_route&&t),document.body.classList.toggle("retail-shop-home-active",o),retail_shop.decorate_retail_workspace()};retail_shop.patch_home_route=function(){var t;if(!retail_shop.should_filter_home_workspace())return;let e=(t=frappe.router)==null?void 0:t.slug(retail_shop.home_workspace);if(!e)return;frappe.re_route=frappe.re_route||{},frappe.re_route.home=e;let o=new URL(window.location.href);(o.pathname==="/app"||o.pathname==="/app/home")&&(o.pathname=`/app/${e}`,window.history.replaceState({},"",o.toString()))};retail_shop.get_native_card_title=function(e){var o,t,a,r;return((t=(o=e.querySelector(".widget-title .ellipsis"))==null?void 0:o.textContent)==null?void 0:t.trim())||((r=(a=e.querySelector(".widget-title"))==null?void 0:a.textContent)==null?void 0:r.trim())||""};retail_shop.decorate_card_header=function(e,o,t){var s;(s=o.querySelector(".retail-shop-card-kicker-row"))==null||s.remove();let a=document.createElement("div"),r=document.createElement("span"),i=document.createElement("span");a.className="retail-shop-card-kicker-row",r.className="retail-shop-card-kicker",i.className="retail-shop-card-count",r.textContent=t.kicker||"Section",i.textContent=String(e.querySelectorAll(".link-item").length),a.appendChild(r),a.appendChild(i),o.prepend(a)};retail_shop.decorate_link_tile=function(e,o,t){e.classList.add("retail-shop-link-tile"),t&&e.classList.add("retail-shop-link-tile--primary");let a=e.querySelector(".link-text"),r=e.querySelector(".link-content");if(!a||!r)return;let i=e.querySelector(".retail-shop-link-copy");i||(i=document.createElement("span"),i.className="retail-shop-link-copy",a.replaceWith(i),i.appendChild(a)),a.classList.add("retail-shop-link-title");let s=e.querySelector(".retail-shop-link-description");o!=null&&o.description?(s||(s=document.createElement("span"),s.className="retail-shop-link-description",i.appendChild(s)),s.textContent=o.description):s==null||s.remove()};retail_shop.set_active_workspace_tab=function(e,o){!e||(e.dataset.activeSection=o,e.querySelectorAll(".retail-shop-tab").forEach(t=>{t.classList.toggle("is-active",t.dataset.section===o),t.setAttribute("aria-selected",t.dataset.section===o?"true":"false")}),e.querySelectorAll(".retail-shop-tab-panel").forEach(t=>{t.classList.toggle("is-active",t.dataset.section===o)}))};retail_shop.build_tabbed_workspace=function(){var s;let e=document.querySelector(".layout-main-section .codex-editor__redactor");if(!e)return;let o=Array.from(e.querySelectorAll(".ce-block")).filter(n=>n.querySelector(".widget.links-widget-box.retail-shop-card[data-retail-section]"));if(o.length<2)return;let t=e.querySelector(".retail-shop-tabs-shell");t||(t=document.createElement("section"),t.className="retail-shop-tabs-shell",t.innerHTML=`
			<div class="retail-shop-tabs" role="tablist" aria-label="Retail sections"></div>
			<div class="retail-shop-tab-panels"></div>
		`,e.insertBefore(t,o[0]));let a=t.querySelector(".retail-shop-tabs"),r=t.querySelector(".retail-shop-tab-panels"),i=t.dataset.activeSection;a.innerHTML="",o.forEach((n,c)=>{let l=n.querySelector(".widget.links-widget-box.retail-shop-card[data-retail-section]"),p=retail_shop.get_native_card_title(l),d=retail_shop.section_meta[p]||{},_=l.dataset.retailSection||d.slug||frappe.router.slug(p||`section-${c}`),h=document.createElement("button");n.parentElement!==r&&r.appendChild(n),n.classList.add("retail-shop-tab-panel"),n.dataset.section=_,h.type="button",h.className="retail-shop-tab",h.dataset.section=_,h.setAttribute("role","tab"),h.innerHTML=`<span class="retail-shop-tab-title">${p}</span>`,h.addEventListener("click",()=>retail_shop.set_active_workspace_tab(t,_)),a.appendChild(h)}),retail_shop.set_active_workspace_tab(t,i&&r.querySelector(`.retail-shop-tab-panel[data-section="${i}"]`)?i:o[0].dataset.section||((s=o[0].querySelector(".widget.links-widget-box"))==null?void 0:s.dataset.retailSection))};retail_shop.decorate_native_workspace_cards=function(e){document.querySelectorAll(".layout-main-section .widget.links-widget-box").forEach(t=>{var n,c;let a=retail_shop.get_native_card_title(t),r=retail_shop.section_meta[a],i=t.querySelector(".widget-body"),s=t.querySelector(".widget-head");if(t.classList.remove("retail-shop-card","retail-shop-card--primary","retail-shop-card--secondary","retail-shop-card--sales-counter","retail-shop-card--back-office","retail-shop-card--reports-audit","retail-shop-card--catalog-contacts"),t.removeAttribute("data-retail-section"),i==null||i.classList.remove("retail-shop-card-body"),t.querySelectorAll(".link-item").forEach(l=>{l.classList.remove("retail-shop-link-tile","retail-shop-link-tile--primary")}),(n=t.querySelector(".retail-shop-card-description"))==null||n.remove(),(c=t.querySelector(".retail-shop-card-kicker-row"))==null||c.remove(),!(!e||!r)){if(t.classList.add("retail-shop-card"),t.classList.add(r.primary?"retail-shop-card--primary":"retail-shop-card--secondary"),t.classList.add(`retail-shop-card--${r.slug}`),t.dataset.retailSection=r.slug,i==null||i.classList.add("retail-shop-card-body"),s&&(retail_shop.decorate_card_header(t,s,r),r.description)){let l=document.createElement("div");l.className="retail-shop-card-description",l.textContent=r.description,s.appendChild(l)}t.querySelectorAll(".link-item").forEach(l=>{var _,h;let p=((h=(_=l.querySelector(".link-text"))==null?void 0:_.textContent)==null?void 0:h.trim())||"",d=retail_shop.link_meta[p];retail_shop.decorate_link_tile(l,typeof d=="string"?{description:d}:d,r.primary)})}})};retail_shop.patch_boot_workspaces=function(){var e;if(!(retail_shop.boot_workspaces_patched||!retail_shop.should_filter_home_workspace())){if(!Array.isArray((e=frappe.boot)==null?void 0:e.allowed_workspaces)){setTimeout(retail_shop.patch_boot_workspaces,50);return}frappe.boot.allowed_workspaces=retail_shop.filter_boot_workspaces(frappe.boot.allowed_workspaces),retail_shop.boot_workspaces_patched=!0}};retail_shop.patch_workspace_sidebar=function(){var o;if(retail_shop.workspace_sidebar_patched||!retail_shop.should_filter_home_workspace()||!((o=frappe.views)!=null&&o.Workspace))return;let e=frappe.views.Workspace.prototype.get_pages;frappe.views.Workspace.prototype.get_pages=function(){return Promise.resolve(e.call(this)).then(t=>(t!=null&&t.pages&&(t.pages=retail_shop.filter_workspace_pages(t.pages)),t))},retail_shop.clear_stale_workspace_state(),retail_shop.workspace_sidebar_patched=!0};retail_shop.patch_workspace_show_page=function(){var o;if(retail_shop.workspace_show_page_patched||!retail_shop.should_filter_home_workspace()||!((o=frappe.views)!=null&&o.Workspace))return;let e=frappe.views.Workspace.prototype.show_page;frappe.views.Workspace.prototype.show_page=async function(...t){let a=await e.apply(this,t);return window.requestAnimationFrame(()=>retail_shop.sync_workspace_page_state()),window.setTimeout(()=>retail_shop.sync_workspace_page_state(),80),a},retail_shop.workspace_show_page_patched=!0};retail_shop.decorate_retail_workspace=function(){var e,o;if(!retail_shop.decorating_workspace){retail_shop.decorating_workspace=!0,(e=retail_shop.workspace_widget_observer)==null||e.disconnect();try{let t=document.body.classList.contains("retail-shop-home-active")||retail_shop.is_retail_workspace_surface();if(retail_shop.decorate_native_workspace_cards(t),retail_shop.unwrap_workspace_sections(),!t)return;retail_shop.wrap_workspace_sections(),retail_shop.build_tabbed_workspace(),document.querySelectorAll(".layout-main-section .widget.shortcut-widget-box").forEach(a=>{var n,c;let r=((c=(n=a.querySelector(".widget-title"))==null?void 0:n.textContent)==null?void 0:c.trim())||"",i=a.closest(".retail-shop-section-card"),s=(i==null?void 0:i.dataset.section)==="sales-counter"&&retail_shop.primary_shortcuts.has(r);a.classList.toggle("retail-shop-primary-shortcut",s),a.classList.toggle("retail-shop-secondary-shortcut",Boolean(r)&&!s)})}finally{retail_shop.decorating_workspace=!1,(o=retail_shop.workspace_widget_observer)==null||o.observe(document.body,{childList:!0,subtree:!0})}}};retail_shop.unwrap_workspace_sections=function(){document.querySelectorAll(".retail-shop-section-card").forEach(e=>{let o=e.parentElement;if(!o)return;Array.from(e.querySelectorAll(":scope > .retail-shop-section-card__header > .ce-block, :scope > .retail-shop-section-card__body > .ce-block")).forEach(a=>o.insertBefore(a,e)),e.remove()})};retail_shop.wrap_workspace_sections=function(){let e=document.querySelector(".layout-main-section .codex-editor__redactor");if(!e)return;let o=null;Array.from(e.children).forEach(t=>{var i;if(!t.classList.contains("ce-block"))return;let a=t.querySelector(".ce-header"),r=Boolean(t.querySelector(".widget.spacer"));if(t.classList.remove("retail-shop-section-break"),a){let s=((i=a.textContent)==null?void 0:i.trim())||"",n=retail_shop.section_meta[s],c=(n==null?void 0:n.slug)||frappe.router.slug(s||"section"),l=document.createElement("section"),p=document.createElement("div"),d=document.createElement("div");if(l.className=`retail-shop-section-card retail-shop-section-card--${c}`,l.dataset.section=c,p.className="retail-shop-section-card__header",d.className="retail-shop-section-card__body",e.insertBefore(l,t),l.appendChild(p),l.appendChild(d),p.appendChild(t),n!=null&&n.description){let _=document.createElement("p");_.className="retail-shop-section-card__note",_.textContent=n.description,p.appendChild(_)}o=d;return}if(r){t.classList.add("retail-shop-section-break"),o=null;return}o&&o.appendChild(t)})};retail_shop.schedule_workspace_decoration=function(){retail_shop.workspace_decoration_scheduled||(retail_shop.workspace_decoration_scheduled=!0,window.requestAnimationFrame(()=>{retail_shop.workspace_decoration_scheduled=!1,retail_shop.decorate_retail_workspace()}))};retail_shop.observe_workspace_widgets=function(){retail_shop.workspace_widget_observer||(retail_shop.workspace_widget_observer=new MutationObserver(()=>{retail_shop.schedule_workspace_decoration()}),retail_shop.workspace_widget_observer.observe(document.body,{childList:!0,subtree:!0}))};retail_shop.init_workspace_customizations=function(){var e;retail_shop.ensure_workspace_styles(),retail_shop.clear_stale_workspace_state(),retail_shop.patch_home_route(),retail_shop.patch_boot_workspaces(),retail_shop.patch_workspace_sidebar(),retail_shop.patch_workspace_show_page(),retail_shop.observe_workspace_widgets(),retail_shop.sync_workspace_page_state(),(e=frappe.after_ajax)==null||e.call(frappe,()=>retail_shop.sync_workspace_page_state())};retail_shop.patch_logout_redirect=function(){!retail_shop.should_filter_home_workspace()||!frappe.app||(frappe.app.redirect_to_login=function(){let e=window.location.pathname+window.location.search;window.location.href=`/retail-login?redirect_to=${encodeURIComponent(e)}`})};localStorage.getItem("session_last_route")==="/app/erpnext-settings"&&localStorage.removeItem("session_last_route");localStorage.getItem("current_page")==="ERPNext Settings"&&(localStorage.removeItem("current_page"),localStorage.removeItem("is_current_page_public"));if($(".dropdown-help").length)retail_shop.hide_help_dropdown_for_non_technical_users();else{let e=new MutationObserver(()=>{$(".dropdown-help").length&&(retail_shop.hide_help_dropdown_for_non_technical_users(),e.disconnect())});e.observe(document.body,{childList:!0,subtree:!0})}var m,u;(u=(m=frappe.router)==null?void 0:m.on)==null||u.call(m,"change",retail_shop.sync_workspace_page_state);document.readyState==="loading"?document.addEventListener("DOMContentLoaded",()=>retail_shop.init_workspace_customizations(),{once:!0}):window.setTimeout(()=>retail_shop.init_workspace_customizations(),0);window.setTimeout(()=>retail_shop.patch_logout_redirect(),0);})();
//# sourceMappingURL=retail_shop.bundle.QVY6NC3B.js.map
