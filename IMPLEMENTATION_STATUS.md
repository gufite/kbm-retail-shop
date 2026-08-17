# Implementation Status

## DONE

- Bench/site inspection completed for:
  - Frappe `15.113.4`
  - ERPNext `15.115.0`
  - Python `3.14.6`
  - Node `18.20.8`
  - `developer_mode` enabled
- Custom app `retail_shop` created and installed
- Core DocTypes:
  - `Electrician` (with optional per-electrician commission override)
  - `Retail Commission Settings`
  - `Retail Shop Settings` (electrician selection is optional by default; a toggle makes it mandatory)
  - `Purchase Entry` / `Purchase Entry Item` (payment status/paid/outstanding tracking, UOM + conversion factor support)
  - `Commission Payment` (tracks commission disbursed to electricians, separate from commission earned)
  - `Retail Audit Log` (append-only; written by hooks on sale cancel, inventory adjustment, commission-setting change, user role change)
- Sales commission snapshots wired into `POS Invoice` and `Sales Invoice`; skipped entirely when no electrician is linked; resolves electrician-level override before falling back to global `Retail Commission Settings`; basis is `grand_total - taxes` so it reflects discounts applied at either item or order level
- Proportional return commission reversal implemented; direct sale cancellation writes an audit log entry (reports/dashboards already exclude cancelled docs via `docstatus=1` filters)
- Credit sales require a real (non-walk-in) customer to be selected
- Stock Reconciliation requires an adjustment reason and is restricted to Retail Administrator; submission is logged to the audit log
- `Stock Settings.valuation_method` defaulted to Moving Average (weighted average)
- Salesperson role can no longer cancel/amend submitted `POS Invoice`/`Sales Invoice` — only Retail Administrator can void or correct a sale; permission application is now idempotent on every migrate (explicitly zeroes unlisted rights instead of leaving stale grants)
- Split-payment credit collection API (`record_credit_payments`) for collecting an outstanding balance across multiple payment methods in one call
- Setup helpers added for: roles, walk-in customer, default modes of payment, custom fields, permissions, stock valuation method
- Dashboard API extended: commission earned/paid/outstanding split, total customer balance due, total supplier balance owed
- Daily scheduled job notifies Retail Administrator users of low/out-of-stock items
- Dedicated retail workspace implemented, including the new doctypes/reports
- Script reports implemented: Sales, Purchase, Profit, Inventory Valuation, Fast/Slow Moving Products, Electrician Commission (now with paid/outstanding columns), Customer Balance, Supplier Balance
- Test suite covers the above (electrician-optional default + toggle, commission override, purchase payment-status transitions, salesperson cancel restriction, commission payment ledger, customer/supplier balances, audit log on cancel, stock reconciliation reason requirement)

## IN PROGRESS

- End-to-end verification on the actual target site `retail.localhost` (previously only exercised on `erp.localhost`)

## TODO

- More opinionated credit-sales UI workflow on top of the existing APIs
- Additional coverage for report totals and profit edge cases

## BLOCKED

- None
