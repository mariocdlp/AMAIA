# Accounting System — Party & Event Rental

Books for a party/event rental business that began operations **April 2026**.

| Decision | Setting |
|---|---|
| Basis | Cash basis, with deposit liability tracking |
| Fiscal period | First period is partial: April 2026 – December 2026 |
| Deliverable | Google Sheets workbook (built as `.xlsx`, converted on upload) |
| Source data | 2 credit cards + 1 checking account, CSV export |

## Why this shape

### Rental fleet is a fixed asset, not inventory

The tables, chairs, tents and linens you rent are **capitalized** (accounts 1510–1550) and
depreciated over their useful life. They are not inventory, because inventory is consumed or
sold and these are retained and re-rented. Expensing a $12,000 chair purchase in the month you
bought it would show a catastrophic April and an unrealistically profitable summer — and it
would understate the balance sheet by the value of the entire fleet.

Inventory accounts (1210–1230) still exist, for the things that genuinely are inventory:
consumables burned per event, goods resold outright, and replacement parts.

### Customer deposits are a liability, not revenue

Account **2210** is the one most rental operators get wrong. A retainer taken in May for an
October wedding is *cash you hold but have not earned*. It belongs on the balance sheet as a
liability and converts to revenue on the event date. Without this, summer looks wildly
profitable and autumn looks broken, and cash flow gets read as performance.

Account **2220** holds refundable damage deposits, which are never revenue — they are returned
or applied against account 4400.

### Sales tax collected is a liability, not revenue

In Texas, rental of tangible personal property is taxable. Deposits landing in checking are
**gross** — they include tax you are merely holding for the state. Account **2300** carries it.
Revenue accounts are recorded net of tax. Skipping this overstates revenue and hides a real debt.

### Interaccount transfers must net to zero

Account **9010** exists to catch the single largest error in multi-account CSV ingestion: paying
a credit card from checking appears **twice** — as an outflow in the checking file and as a
payment in the card file. Neither is an expense. The actual expense was recorded when the card
was swiped. Every transfer is tagged 9010 and excluded from both the P&L and the cash flow
operating section.

## Statements produced

1. **Cash Flow** — operating / investing / financing, reconciled to actual combined bank balance
2. **Balance Sheet** — assets, liabilities, equity, proving Assets = Liabilities + Equity
3. **Revenue & Expenditure (P&L)** — revenue → COGS → gross margin → opex → net income

Gross margin matters here specifically: it separates what each event costs to deliver
(sub-rentals, fuel, crew, laundering) from what the business costs to keep open (rent,
insurance, software). A rental business can be busy and unprofitable, and only the margin line
shows it.

## Open decisions

These need your input before the books close. They do not block categorization.

- **Capitalization threshold** — the dollar line above which a purchase is an asset rather than
  an expense. IRS de minimis safe harbor allows up to $2,500 per item. Note that 200 chairs at
  $8 each is one $1,600 *fleet asset*, not 200 trivial purchases.
- **Depreciation lives** — proposed: rental equipment 5–7 yr, linens 3 yr, vehicles 5 yr,
  leasehold improvements over lease term.
- **Entity type** — LLC, S-corp or sole proprietor. Drives whether owner payments are draws
  (3020) or payroll (6400).
- **Sales tax on delivery** — generally taxable in Texas when the rental is taxable; confirm
  with your CPA.

## Data still needed

Bank CSVs alone **cannot** tell a deposit from earned revenue — a $500 credit is just a $500
credit. Splitting 2210 from 4010 requires event dates. A booking export, invoice list, or even a
calendar of event dates lets this be done properly; without it, all customer receipts are
recognized on the date received and the deposit liability stays empty.
