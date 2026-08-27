# KBM Lighting Trading — User Manual

Version: 27 August 2026

## 1. Purpose of this manual

This manual explains what each retail role is responsible for and how each person should use the system. It covers the current system behavior for:

- Technical Admin
- Shop Admin
- Salesperson

The system intentionally shows only retail-related workspaces. A Salesperson sees the **KBM Lighting Trading** workspace. A Shop Admin or Technical Admin also sees **Staff** and **Store Settings**.

## 2. The basic retail flow

The normal operating sequence is:

1. Configure the store and create staff accounts.
2. Create suppliers, categories, customers, and electricians when needed.
3. Receive products through **Stock In**. A new product can be registered during this step.
4. Confirm available quantities through **Stock Balance**.
5. Sell products through **New Sale** or **Credit Sales**.
6. Review completed transactions through **Sales History** and the reports.
7. Correct physical stock differences through **Stock Count**.
8. Review and pay electrician commissions.

### Important document rule

Saving and submitting are not the same:

- **Draft:** work is saved but has not changed official stock or accounting records.
- **Submitted:** the transaction is final and affects stock, balances, and reports.
- **Cancelled:** an authorized user reversed a submitted transaction.

Always confirm that a completed sale, Stock In, Stock Count, or Commission Payment is **Submitted**.

## 3. Role summary

| Activity | Technical Admin | Shop Admin | Salesperson |
| --- | --- | --- | --- |
| Open the retail workspace | Yes | Yes | Yes |
| Make cash/POS sales | Yes | Yes | Yes |
| Create credit sales | Yes | Yes | Yes |
| View stock balance | Yes | Yes | Yes |
| Register and edit products | Yes | Yes | View only |
| Receive products through Stock In | Yes | Yes | No |
| Perform stock counts/corrections | Yes | Yes | No |
| Create and edit suppliers | Yes | Yes | View only |
| Create and edit customers | Yes | Yes | Yes |
| Create and edit electricians | Yes | Yes | View only |
| Pay electrician commission | Yes | Yes | View only |
| View all management reports and audit logs | Yes | Yes | Limited reports |
| Change store and commission settings | Yes | Yes | No |
| Create Salesperson accounts | Yes | Yes | No |
| Create Shop Admin or Technical Admin accounts | Yes | No | No |
| Reset or disable managed staff accounts | Yes | Salesperson accounts only | No |
| Cancel or correct completed sales | Yes | Yes | No |

The Technical Admin should normally avoid doing ordinary cashier work. The role has broad access so that it can configure, support, and recover the system.

## 4. Signing in and navigating

1. Open the KBM Lighting Trading login page.
2. Enter the assigned **Username** and **Password**.
3. Select **Login**.
4. The system opens the **KBM Lighting Trading** workspace.
5. Select the relevant workspace tab:
   - **Sales Counter** for sales and stock lookup
   - **Back Office** for stock and commission operations
   - **Reports & Audit** for management information
   - **Catalog & Contacts** for products and business contacts

Shop Admin and Technical Admin can use the left menu to open **Staff** and **Store Settings**.

### Sign-in rules

- Usernames are not case-sensitive in the onboarding process and are stored in lowercase.
- Never share an account between staff members.
- The staff member should receive the username and password directly from an authorized admin.
- No welcome email is sent when an account is created.
- Report a forgotten or exposed password to a Shop Admin or Technical Admin immediately.

## 5. Salesperson manual

The Salesperson handles customer sales and basic customer service. The Salesperson can adjust the selling price during checkout, but cannot sell below the Minimum Selling Price set by a manager. The Salesperson cannot change stock records, product price limits, suppliers, commissions, or store configuration.

### 5.1 Start the selling day

1. Sign in with your own account.
2. Open **Sales Counter → New Sale**.
3. If the system requests a POS opening entry, select the assigned POS profile and company, enter the opening cash amount, and submit the opening entry.
4. Confirm that products and prices appear in the POS screen.
5. Use **Stock Balance** if a customer asks whether an item is available.

### 5.2 Make a normal counter sale

1. Open **Sales Counter → New Sale**.
2. Search for or select each product.
3. Enter the quantity being sold.
4. Confirm or adjust the **Selling Price** for each product. The system will reject a price below the product's Minimum Selling Price.
5. Use the default walk-in customer for an ordinary fully paid counter sale.
6. Select **Checkout**.
7. If a discount is approved, enter it in **Transaction Discount** as a fixed money amount. Do not calculate or enter a percentage. The amount applies once to the whole transaction.
8. If an electrician referred the customer, select the electrician in Additional Information.
9. Select the payment method, such as Cash, Bank Transfer, or Mobile Money.
10. Confirm that the payment amount equals the amount collected.
11. Complete and submit the sale.
12. Print or provide the receipt when required.

The system distributes the transaction discount across the products and checks each final price. If any product would fall below its Minimum Selling Price, reduce the discount or increase that product's Selling Price.

The commission shown on the sale is calculated by the system. A Salesperson must not try to calculate or edit it manually.

### 5.3 Make a credit sale

Credit sales must be linked to the real customer who owes the balance.

1. Open **Sales Counter → Credit Sales**.
2. Create a new Sales Invoice.
3. Select an existing customer or create the customer first.
4. Do not use the walk-in customer for a credit sale.
5. Add each product and quantity.
6. Confirm or adjust each **Selling Price** without going below the product's Minimum Selling Price.
7. Enter any approved **Transaction Discount** as one fixed amount for the invoice, not as a percentage or item-level discount.
8. Make sure **Update Stock** is enabled so the sold quantity leaves inventory.
9. Confirm the due date or payment schedule.
10. Select the electrician when applicable.
11. Save and submit the invoice.
12. If the customer pays an amount immediately, record that payment against the submitted invoice.
13. Confirm that the invoice shows the correct remaining outstanding amount.

When the customer later pays, open the submitted credit invoice and record the payment against that invoice using the available payment action. Never create a second sale to represent collection of an old debt. The payment must not exceed the outstanding balance.

### 5.4 Review a completed sale

1. Open **Sales Counter → Sales History** for POS transactions or **Credit Sales** for credit invoices.
2. Search by sale reference, date, customer, or status.
3. Open the transaction to inspect products, payment, electrician, and totals.
4. Print the transaction when required.

A Salesperson cannot cancel or amend a submitted sale. If a sale is wrong or goods are returned, stop and request a Shop Admin.

### 5.5 Create or update a customer

1. Open **Catalog & Contacts → Customer**.
2. Select **Add Customer** or open an existing customer.
3. Enter a clear customer name and the available contact details.
4. Save the record.

A real customer record is mandatory for a credit sale. Avoid creating duplicates with slightly different spelling.

### 5.6 Information available to a Salesperson

Depending on the selected tab, the Salesperson can read:

- Stock Balance
- Products and Categories
- Customers and Suppliers
- Electricians
- Sales Report
- Inventory Valuation
- Electrician Commission Report
- Existing Commission Payments

These screens are for checking information. Administrative changes remain restricted.

### 5.7 End the selling day

1. Finish and submit all genuine sales.
2. Check for drafts that should either be completed or removed.
3. Review **Sales History** against receipts and collected money.
4. Complete the POS closing entry when the POS screen requires it.
5. Report price, stock, payment, or customer-balance differences to the Shop Admin.
6. Sign out before leaving the device.

## 6. Shop Admin manual

The Shop Admin controls daily store operations. This role performs all Salesperson tasks and also manages products, receiving, stock corrections, suppliers, electricians, commissions, reports, settings, and Salesperson accounts.

### 6.1 Register a new product and receive its first quantity

The preferred method is **Stock In**, because product registration and physical quantity are recorded together.

1. Open **Back Office → Stock In**.
2. Select the supplier.
3. Confirm the purchase date. It defaults to today.
4. Add a row under **Products**.
5. Enter a unique **Product Code**.
6. For a new code, enter the **Product Description**.
7. Enter the **Purchase Unit Price**.
8. Enter the **Quantity Purchased**.
9. Enter the **Selling Unit Price**.
10. Enter the **Minimum Selling Price**. It must be greater than zero and cannot exceed the Selling Unit Price.
11. Add further products when the same supplier delivery contains multiple items.
12. Enter the amount paid to the supplier at this time:
    - zero produces **Unpaid**
    - less than the total produces **Partial**
    - the full total produces **Paid**
13. Review total quantity, total amount, paid amount, and outstanding amount.
14. Save and submit the Stock In document.

On submission, the system creates the official Purchase Receipt, increases stock in the default warehouse, and updates the purchase and selling prices.

### 6.2 Restock an existing product

1. Open **Back Office → Stock In**.
2. Enter the existing Product Code.
3. The system loads the existing description and recent prices, including the Minimum Selling Price.
4. Enter the newly purchased quantity and confirm the purchase, selling, and minimum prices.
5. Submit the Stock In document.

The system adds the new quantity to current stock. It does not create a duplicate product, and it does not replace the existing product description with text entered on the Stock In row.

### 6.3 Register product information without stock

Use **Catalog & Contacts → Products** only when the product master must exist before stock arrives.

1. Select **Add Product**.
2. Enter Product Code, Product Name, Category, Unit, Selling Unit Price, and Minimum Selling Price.
3. Save the product.

This creates product information but does not create sellable quantity. Use **Stock In** when the physical items arrive. Never type a quantity directly into the product master as a replacement for Stock In.

### 6.4 Manage categories

1. Open **Catalog & Contacts → Categories**.
2. Search before creating a category to avoid duplicates.
3. Create categories using simple shop language, such as Bulbs, Switches, Cable, or Fixtures.
4. Save the category.

The default category in Store Settings is used when Stock In automatically creates a new product.

### 6.5 Manage suppliers

1. Open **Catalog & Contacts → Supplier**.
2. Search for the supplier before creating a new record.
3. Add or update the supplier's name and contact details.
4. Save the supplier.
5. Use the supplier on every Stock In transaction.

Use **Supplier Balance Report** to review unpaid purchase amounts recorded during Stock In.

### 6.6 Perform a stock count or correction

Stock Count is for correcting a difference between physical stock and system stock. It is not the normal way to receive purchases.

1. Physically count the selected products.
2. Open **Back Office → Stock Count**.
3. Confirm the Count Date and Count Time.
4. Enter a meaningful **Reason**, such as “Monthly physical count” or “Correcting damaged units.” A reason is mandatory.
5. Add each Product Code.
6. Compare **System Quantity** with the physical count.
7. Enter the physical value as **Counted Quantity**.
8. Review every row carefully.
9. Save and submit the Stock Count.

Submission updates inventory to the counted quantity and creates an Inventory Adjustment entry in the Retail Audit Log.

### 6.7 Manage electricians

1. Open **Catalog & Contacts → Electrician**.
2. Enter the electrician's name and optional mobile number.
3. Keep **Active** selected while the electrician is eligible for sales commissions.
4. Leave Commission Override Type blank to use the store-wide commission rule.
5. To give this electrician a special rule, choose Percentage or Fixed Amount and enter the value.
6. Save the record.

Inactive electricians cannot be attached to new sales.

### 6.8 Configure commissions

1. Open **Store Settings → Retail Commission Settings**.
2. Select Percentage or Fixed Amount.
3. Enter the corresponding rate or amount.
4. Save the settings.

The percentage cannot exceed 100%, and fixed amounts cannot be negative. The rule is captured when a sale is submitted, so changing the settings does not silently recalculate historical sales.

### 6.9 Pay electrician commission

1. Review **Reports & Audit → Electrician Commission Report**.
2. Find the electrician and review Net Commission, Commission Paid, and Commission Outstanding.
3. Decide the exact commission period being paid and verify that it does not duplicate an earlier payment period.
4. Open **Back Office → Commission Payment**.
5. Create a new payment.
6. Select the electrician and the From Date/To Date covered by the payment.
7. Confirm the calculated Commission Earned.
8. Enter Amount Paid, Payment Date, Mode of Payment, and optional remarks.
9. Save and submit.

The system prevents a payment greater than the outstanding commission for the selected period. Returns reduce the commission earned from the original sale proportionally.

### 6.10 Onboard a Salesperson

1. Open **Staff → Users**.
2. Select **New Staff**.
3. Enter a unique Username using letters, numbers, dot, dash, or underscore.
4. Confirm that the role is **Salesperson**. A Shop Admin cannot assign Shop Admin or Technical Admin.
5. Enter Email only when the staff member has one. Email is optional.
6. Enter a Password of at least six characters.
7. Enter the same value in Confirm Password.
8. Select **Create Staff Account**.
9. Give the username and password to the staff member directly.
10. Ask the staff member to sign in before starting work.

No email is sent. When email is blank, the system creates an internal address so the account can still work with a username.

### 6.11 Manage an existing Salesperson account

From **Staff → Users**, a Shop Admin can:

- see the account status and last login
- disable a former or suspended Salesperson
- enable a disabled Salesperson
- set a new password

A Shop Admin cannot manage Technical Admin or other Shop Admin accounts and cannot disable their own account.

### 6.12 Correct a completed sale

1. Open the original transaction from Sales History or Credit Sales.
2. Verify the customer, products, quantities, payment, and submission status.
3. Use the proper return or cancellation process. Do not create an unrelated negative sale.
4. Enter the reason when the interface requests one.
5. Confirm the resulting stock, customer balance, payment, and commission effect.

Cancelled sales linked to an electrician are recorded in the Retail Audit Log. A return reverses the original commission proportionally.

### 6.13 Daily and periodic reports

The Shop Admin can use:

- **Sales Report:** sales by date, salesperson, electrician, payment method, commission, and status
- **Profit Report:** revenue, cost, gross profit, and gross margin by product/category
- **Inventory Valuation:** quantity, valuation rate, and inventory value by product
- **Customer Balance Report:** outstanding customer credit balances
- **Supplier Balance Report:** unpaid supplier amounts from Stock In
- **Purchase Report:** submitted purchases by date, supplier, product, quantity, and cost
- **Electrician Commission Report:** earned, returned, paid, and outstanding commission
- **Retail Audit Log:** sensitive events such as inventory adjustments, sale cancellations, and settings changes

Use the report controls that are available on the screen and verify the displayed period before making decisions or exporting information.

### 6.14 Shop Admin daily checklist

At opening:

- Review low-stock and out-of-stock notifications.
- Confirm the POS can open and products have valid prices.
- Check urgent customer and supplier balances.

During the day:

- Submit every genuine Stock In transaction.
- Investigate stock differences instead of silently changing quantities.
- Review requested sale returns or cancellations.
- Create and disable Salesperson accounts promptly when staffing changes.

At closing:

- Compare sales reports with cash and electronic collections.
- Check outstanding customer credit.
- Check drafts that were not submitted.
- Review unusual audit-log entries.

## 7. Technical Admin manual

The Technical Admin protects the system structure and handles access that a Shop Admin must not control. This role can also perform Shop Admin work when recovery or support requires it.

### 7.1 Initial store configuration

1. Open **Store Settings → Retail Shop Settings**.
2. Confirm Default Company.
3. Confirm Default Warehouse.
4. Confirm Default Category for New Products.
5. Confirm Default Walk-in Customer.
6. Confirm the currency.
7. Decide whether every sale must include an electrician using **Require Electrician**.
8. Save the settings.
9. Configure the default commission rule.
10. Confirm the accepted modes of payment and their accounting defaults.

Incorrect company, warehouse, category, or payment-account defaults can stop Stock In or POS submission. Test the complete Stock In and sale flow after configuration changes.

### 7.2 Create privileged staff accounts

1. Open **Staff → Users**.
2. Select **New Staff**.
3. Enter Username.
4. Select Technical Admin, Shop Admin, or Salesperson.
5. Enter optional Email.
6. Enter and confirm a password of at least six characters.
7. Create the account and communicate the credentials securely.

Assign the lowest role that allows the person to do their job:

- Cashier or sales clerk → Salesperson
- Store manager → Shop Admin
- System owner/support administrator → Technical Admin

### 7.3 Manage privileged accounts

The Technical Admin can reset passwords and enable or disable managed shop accounts. The protected Administrator account cannot be disabled. Never disable the last working Technical Admin account without first confirming another recovery account.

### 7.4 Technical operations

The Technical Admin is responsible for:

- maintaining secure administrator credentials
- applying approved application updates and migrations
- ensuring backups run successfully
- testing that backups can be restored
- checking background jobs and stock notifications
- investigating permission or login problems
- protecting database and server access
- testing critical flows after configuration or software changes

Technical system work should not be done from a Salesperson or shared account.

### 7.5 Technical Admin periodic checklist

- Confirm backups are recent and restorable.
- Review active users and disable accounts that are no longer needed.
- Review privileged roles for unnecessary access.
- Confirm default company, warehouse, category, customer, currency, and payment modes.
- Review Retail Audit Log activity with the Shop Admin.
- Test one product receipt, one sale, one credit sale, one stock count, and one commission report after major updates.

## 8. Product and inventory rules

1. Product Code must uniquely identify one product.
2. Do not create multiple codes for the same physical item without a business reason.
3. Product information and stock quantity are different:
   - Products defines what the item is.
   - Stock In defines how many units arrived and their cost.
   - Sales reduce the quantity.
   - Returns add returned quantity according to the return transaction.
   - Stock Count corrects differences after physical verification.
4. Never use Stock Count as a substitute for Stock In.
5. Never alter quantity outside an official stock transaction.
6. Do not sell when available stock is zero or insufficient.
7. Verify purchase and selling prices during every Stock In transaction.

## 9. Common problems and responses

### Product cannot be sold

- Check Stock Balance.
- Confirm the Stock In document was submitted.
- Confirm the product is not marked Inactive.
- Ask the Shop Admin to check the default warehouse and selling price.

### A new Product Code cannot be created during Stock In

- Enter Product Description.
- Confirm Purchase Unit Price, Quantity Purchased, and Selling Unit Price.
- Ask the Shop Admin or Technical Admin to confirm Default Category and Default Warehouse.

### Credit sale is rejected

- Select a real customer instead of the walk-in customer.
- Confirm Update Stock is enabled.
- Confirm there is sufficient stock.
- Confirm required dates and accounting fields are available.

### Electrician cannot be selected

- Confirm the electrician exists.
- Ask the Shop Admin to confirm the electrician is Active.

### Staff member cannot sign in

- Confirm the exact username.
- Confirm the account is Active.
- Reset the password from Staff → Users.
- Confirm the password has at least six characters.
- Escalate persistent login or permission problems to the Technical Admin.

### Wrong submitted sale

- Do not delete or hide the transaction.
- Do not create an unrelated transaction to force the totals to match.
- Record the reference and notify a Shop Admin for cancellation, amendment, or return.

### Physical stock differs from the system

- Recount the product.
- Review recent Stock In, sales, returns, and drafts.
- Use Stock Count only after the reason for the difference is understood and documented.

## 10. Responsibility and escalation

- Salesperson reports operational errors to the Shop Admin.
- Shop Admin resolves normal retail, stock, pricing, customer, supplier, and commission issues.
- Technical Admin resolves account, permission, configuration, deployment, backup, and system failures.
- Any suspicious login, unexplained stock change, missing transaction, or unexpected audit entry must be escalated immediately.
