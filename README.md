# Retail Shop

Custom Frappe/ERPNext v15 app for a single-shop sales and inventory workflow.

## Architecture

- Standard ERPNext documents remain the source of truth for stock and accounting.
- `POS Invoice` is treated as the primary POS transaction on this installed ERPNext version.
- `Sales Invoice` with `update_stock = 1` is supported for credit-style retail sales and return handling.
- `Purchase Entry` is a simplified custom DocType that submits a standard `Purchase Receipt`.
- Commission snapshots are stored on submitted sales documents through custom fields.
- A public `Retail Shop` workspace provides the main Desk entry point for daily use.

## Included Components

- Custom DocTypes:
  - `Electrician`
  - `Retail Commission Settings`
  - `Retail Shop Settings`
  - `Purchase Entry`
  - `Purchase Entry Item`
- Custom sales fields on `POS Invoice` and `Sales Invoice`:
  - `custom_electrician`
  - `custom_commission_type`
  - `custom_commission_rate`
  - `custom_commission_basis_amount`
  - `custom_commission_amount`
- Reports:
  - `Sales Report`
  - `Purchase Report`
  - `Profit Report`
  - `Electrician Commission Report`
  - `Fast Moving Products`
  - `Slow Moving Products`
  - `Inventory Valuation`
- APIs:
  - `retail_shop.api.dashboard.get_dashboard_data`
  - `retail_shop.api.sales.record_credit_payment`
  - `retail_shop.api.sales.get_sale_summary`
  - `retail_shop.api.purchases.make_purchase_entry`

## Setup

1. Install ERPNext v15 first.
2. Install the app on the target site:

```bash
bench --site <site> install-app retail_shop
```

3. Migrate:

```bash
bench --site <site> migrate
```

4. Verify and adjust:
   - `Retail Shop Settings`
   - `Retail Commission Settings`
   - default warehouse
   - default walk-in customer
   - modes of payment: `Cash`, `Bank Transfer`, `Mobile Money`, `Credit`

## Behavior Notes

- Stock movements are standard ERPNext transactions only:
  - purchase stock-in via `Purchase Receipt`
  - sales stock-out via `POS Invoice` or `Sales Invoice`
  - returns via ERPNext return documents
  - stock taking via `Stock Reconciliation`
- Commission basis uses `net_total` on the sales document.
- Returns reverse commission proportionally from the original sale snapshot.
- Historical commission snapshots are not recalculated when settings change.

## Roles

- `Technical Admin`
  - system setup, raw user accounts, and Frappe/ERPNext configuration
  - can create Shop Admin and Salesperson users
- `Shop Admin`
  - manages products, stock in, stock count, electricians, settings, and reports
  - can create, enable, disable, and reset passwords for Salesperson accounts
  - cannot change system settings or Technical Admin / Shop Admin accounts
- `Salesperson`
  - can submit sales and read retail reports
  - cannot change commission settings
  - cannot create stock counts or purchase entries

## Testing

Run:

```bash
bench --site <site> run-tests --app retail_shop
```

## Operations

Migration and cache refresh:

```bash
bench --site <site> migrate
bench --site <site> clear-cache
```
# kbm-retail-shop
