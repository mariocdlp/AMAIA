"""Build the Google Sheets workbook (written as .xlsx, converted by Drive on upload)."""
import json, csv, os, collections, datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(BASE, "out")
M = '#,##0.00;[Red](#,##0.00)'
PCT = '0.0%'

INK   = "1A1A2E"; ACCENT = "0F5C4A"; MUTED = "6B7280"
HDR   = PatternFill("solid", fgColor="0F5C4A")
BAND  = PatternFill("solid", fgColor="F2F5F4")
WARN  = PatternFill("solid", fgColor="FDF1DC")
TOTAL = PatternFill("solid", fgColor="E6EDEB")
THIN  = Side(style="thin", color="D5DBD9")


def title(ws, text, sub=""):
    ws["A1"] = text; ws["A1"].font = Font(bold=True, size=16, color=INK)
    if sub:
        ws["A2"] = sub; ws["A2"].font = Font(size=10, italic=True, color=MUTED)
    ws.freeze_panes = "A4"


def header(ws, row, cols, widths=None):
    for i, c in enumerate(cols, 1):
        cell = ws.cell(row=row, column=i, value=c)
        cell.font = Font(bold=True, color="FFFFFF", size=10)
        cell.fill = HDR
        cell.alignment = Alignment(horizontal="left" if i == 1 else "right", vertical="center")
    ws.row_dimensions[row].height = 22
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w


def line(ws, row, label, value, bold=False, money=True, indent=0, fill=None, note=None):
    c = ws.cell(row=row, column=1, value=("    " * indent) + label)
    c.font = Font(bold=bold, size=10, color=INK)
    v = ws.cell(row=row, column=2, value=value)
    v.font = Font(bold=bold, size=10, color=INK)
    if money:
        v.number_format = M
    if note:
        n = ws.cell(row=row, column=3, value=note)
        n.font = Font(size=9, italic=True, color=MUTED)
    if fill:
        for col in range(1, 4):
            ws.cell(row=row, column=col).fill = fill
    return row + 1


def main():
    st = json.load(open(os.path.join(OUT, "statements.json")))
    led = json.load(open(os.path.join(OUT, "ledger_coded.json")))
    ghl = json.load(open(os.path.join(OUT, "ghl_payments.json")))
    coa = list(csv.DictReader(open(os.path.join(BASE, "chart_of_accounts.csv"))))
    names = {r["code"]: r["account"] for r in coa}

    wb = Workbook(); wb.remove(wb.active)
    rev = st["revenue"]

    # ───────────────────────── Dashboard ─────────────────────────
    ws = wb.create_sheet("Dashboard")
    title(ws, "El Paso Fiesta Tent & Party Rental",
          f"Financial position, inception (April 2026) through {st['period']['end']} · cash basis with deposit tracking")
    ws.column_dimensions["A"].width = 38
    ws.column_dimensions["B"].width = 16
    ws.column_dimensions["C"].width = 54
    r = 4
    r = line(ws, r, "PERFORMANCE", None, bold=True, money=False, fill=TOTAL)
    r = line(ws, r, "Revenue recognized", rev["recognized"], note="Earned by event date, not cash received")
    r = line(ws, r, "Cost of delivering events", -st["total_cogs"])
    r = line(ws, r, "Gross profit", st["gross_profit"], bold=True, fill=BAND)
    ws.cell(row=r-1, column=3, value=f"{st['gross_profit']/rev['recognized']*100:.1f}% margin").font = Font(size=9, italic=True, color=ACCENT)
    r = line(ws, r, "Operating expenses", -st["total_opex"])
    r = line(ws, r, "Other income", st["other_income"], note="Card cash back and bank bonus")
    r = line(ws, r, "NET INCOME", st["net_income"], bold=True, fill=TOTAL)
    r += 1
    r = line(ws, r, "POSITION", None, bold=True, money=False, fill=TOTAL)
    r = line(ws, r, "Cash in checking", st["cash_chase"])
    r = line(ws, r, "Undeposited funds in transit", st["undeposited_funds"], note="Charges taken 9/15-9/17, not yet settled")
    r = line(ws, r, "Rental fleet, net of depreciation", st["fleet_nbv"])
    r = line(ws, r, "Customer deposits held", -st["deferred_revenue"], fill=WARN,
             note="NOT yours yet - owed as events not yet delivered")
    r += 1
    r = line(ws, r, "OWNER", None, bold=True, money=False, fill=TOTAL)
    r = line(ws, r, "Contributions into the business", st["owner_contributions"])
    r = line(ws, r, "Draws taken out", -st["owner_draws"])
    r += 1
    r = line(ws, r, "WHERE THE MONEY WENT", None, bold=True, money=False, fill=TOTAL)
    spend = sorted(({**st["cogs"], **st["opex"]}).items(), key=lambda kv: -kv[1])[:10]
    top = spend[0][1] if spend else 1
    for code, amt in spend:
        ws.cell(row=r, column=1, value="    " + names.get(code, code)).font = Font(size=10, color=INK)
        c = ws.cell(row=r, column=2, value=amt); c.number_format = M; c.font = Font(size=10)
        b = ws.cell(row=r, column=3, value=f'=REPT("■",ROUND({amt/top*30},0))')
        b.font = Font(color=ACCENT, size=9)
        r += 1
    r += 1
    ws.cell(row=r, column=1, value="Read the 'Data Gaps' tab before relying on the balance sheet.").font = Font(size=10, bold=True, color="B45309")

    # ───────────────────────── P&L ─────────────────────────
    ws = wb.create_sheet("Revenue & Expenditure")
    title(ws, "Revenue & Expenditure", f"Inception through {st['period']['end']} · revenue recognized on event date")
    header(ws, 4, ["Account", "Amount", "Notes"], [46, 16, 52])
    r = 5
    r = line(ws, r, "REVENUE", None, bold=True, money=False, fill=TOTAL)
    r = line(ws, r, "Rental & event revenue (events delivered)", rev["earned_by_event"], indent=1)
    r = line(ws, r, "Revenue with no event date on invoice", rev["undated_on_receipt"], indent=1,
             note="Recognized on receipt - add dates to these invoices")
    r = line(ws, r, "Total revenue recognized", rev["recognized"], bold=True, fill=BAND)
    r += 1
    r = line(ws, r, "COST OF DELIVERING EVENTS", None, bold=True, money=False, fill=TOTAL)
    for code, amt in sorted(st["cogs"].items()):
        r = line(ws, r, names.get(code, code), -amt, indent=1,
                 note="Derived: invoiced less net payout" if code == "5090" else None)
    r = line(ws, r, "Total cost of events", -st["total_cogs"], bold=True, fill=BAND)
    r = line(ws, r, "GROSS PROFIT", st["gross_profit"], bold=True, fill=TOTAL,
             note=f"{st['gross_profit']/rev['recognized']*100:.1f}% of revenue")
    r += 1
    r = line(ws, r, "OPERATING EXPENSES", None, bold=True, money=False, fill=TOTAL)
    for code, amt in sorted(st["opex"].items()):
        r = line(ws, r, names.get(code, code), -amt, indent=1,
                 note="Non-cash" if code == "6800" else ("Needs classification" if code == "6990" else None))
    r = line(ws, r, "Total operating expenses", -st["total_opex"], bold=True, fill=BAND)
    r += 1
    r = line(ws, r, "Other income", st["other_income"], indent=1)
    r = line(ws, r, "NET INCOME", st["net_income"], bold=True, fill=TOTAL)

    # ───────────────────────── Balance Sheet ─────────────────────────
    ws = wb.create_sheet("Balance Sheet")
    title(ws, "Balance Sheet", f"As of {st['period']['end']}")
    header(ws, 4, ["Account", "Amount", "Notes"], [46, 16, 56])
    r = 5
    r = line(ws, r, "ASSETS", None, bold=True, money=False, fill=TOTAL)
    r = line(ws, r, "Cash - Chase checking 5784", st["cash_chase"], indent=1)
    r = line(ws, r, "Undeposited funds / in transit", st["undeposited_funds"], indent=1,
             note="Charges taken 9/15-9/17, settling after period end")
    for code, amt in sorted(st["fleet"].items()):
        r = line(ws, r, names.get(code, code), amt, indent=1)
    r = line(ws, r, "Less accumulated depreciation", -st["accumulated_depreciation"], indent=1)
    total_assets = round(st["cash_chase"] + st["undeposited_funds"] + st["fleet_nbv"], 2)
    r = line(ws, r, "TOTAL ASSETS", total_assets, bold=True, fill=BAND)
    r += 1
    r = line(ws, r, "LIABILITIES", None, bold=True, money=False, fill=TOTAL)
    savor = st["card_balances"].get("Capital One Savor 5198", 0)
    r = line(ws, r, "Credit card - Capital One Savor 5198", savor, indent=1)
    r = line(ws, r, "Credit card - Apple Card", 0, indent=1, fill=WARN,
             note="NOT DERIVABLE - export starts 6/1, opening balance unknown")
    r = line(ws, r, "Customer deposits held (events not yet delivered)", st["deferred_revenue"],
             indent=1, fill=WARN, note="8 future events - see Deferred Revenue tab")
    total_liab = round(savor + st["deferred_revenue"], 2)
    r = line(ws, r, "TOTAL LIABILITIES", total_liab, bold=True, fill=BAND,
             note="Understated by the Apple Card balance")
    r += 1
    r = line(ws, r, "EQUITY", None, bold=True, money=False, fill=TOTAL)
    r = line(ws, r, "Owner contributions", st["owner_contributions"], indent=1)
    r = line(ws, r, "Owner draws", -st["owner_draws"], indent=1)
    r = line(ws, r, "Net income for the period", st["net_income"], indent=1)
    eq = round(st["owner_contributions"] - st["owner_draws"] + st["net_income"], 2)
    r = line(ws, r, "Subtotal equity", eq, indent=1)
    plug = round(total_assets - total_liab - eq, 2)
    r = line(ws, r, "Opening balance equity / unreconciled", plug, indent=1, fill=WARN,
             note="The gap from missing Apple Card history - do not ignore")
    r = line(ws, r, "TOTAL LIABILITIES + EQUITY", round(total_liab + eq + plug, 2), bold=True, fill=TOTAL)

    # ───────────────────────── Cash Flow ─────────────────────────
    ws = wb.create_sheet("Cash Flow")
    title(ws, "Cash Flow", "Cash basis: a card charge is treated as spent on the charge date")
    header(ws, 4, ["", "Amount", "Notes"], [46, 16, 56])
    op_in = rev["bank_received"]
    op_out = round(st["total_cogs"] - st["cogs"].get("5090", 0) + st["total_opex"] - st["opex"].get("6800", 0), 2)
    tax = st["sales_tax_remitted"]
    invest = st["fleet_cost"]
    fin = round(st["owner_contributions"] - st["owner_draws"], 2)
    r = 5
    r = line(ws, r, "OPERATING", None, bold=True, money=False, fill=TOTAL)
    r = line(ws, r, "Cash received from customers", op_in, indent=1)
    r = line(ws, r, "Cash paid for events and operations", -op_out, indent=1)
    r = line(ws, r, "Sales tax remitted to Texas", -tax, indent=1)
    r = line(ws, r, "Net operating cash flow", round(op_in - op_out - tax, 2), bold=True, fill=BAND)
    r += 1
    r = line(ws, r, "INVESTING", None, bold=True, money=False, fill=TOTAL)
    r = line(ws, r, "Purchase of rental fleet and equipment", -invest, indent=1)
    r += 1
    r = line(ws, r, "FINANCING", None, bold=True, money=False, fill=TOTAL)
    r = line(ws, r, "Owner contributions", st["owner_contributions"], indent=1)
    r = line(ws, r, "Owner draws", -st["owner_draws"], indent=1)
    r = line(ws, r, "Net financing cash flow", fin, bold=True, fill=BAND)
    r += 1
    r = line(ws, r, "NET CHANGE IN CASH POSITION", round(op_in - op_out - tax - invest + fin, 2), bold=True, fill=TOTAL)
    r += 1
    ws.cell(row=r, column=1, value="Monthly operating cash in vs out").font = Font(bold=True, size=11, color=INK)
    r += 1
    header(ws, r, ["Month", "Cash in", "Cash out", "Net"], [46, 16, 16, 16]); r += 1
    mon_in = collections.defaultdict(float); mon_out = collections.defaultdict(float)
    for t in led:
        if t["account_code"] in ("9010", "3010", "3020"):
            continue
        k = t["date"][:7]
        (mon_in if t["amount"] > 0 else mon_out)[k] += t["amount"]
    for k in sorted(set(mon_in) | set(mon_out)):
        ws.cell(row=r, column=1, value=k)
        for col, val in ((2, mon_in[k]), (3, mon_out[k]), (4, mon_in[k] + mon_out[k])):
            c = ws.cell(row=r, column=col, value=round(val, 2)); c.number_format = M
        r += 1

    # ───────────────────────── Deferred Revenue ─────────────────────────
    ws = wb.create_sheet("Deferred Revenue")
    title(ws, "Customer Deposits Held",
          "Cash received for events that have not happened yet. This is a liability, not income.")
    header(ws, 4, ["Event date", "Invoice", "Customer", "Paid on", "Amount"], [14, 44, 26, 14, 14])
    r = 5
    for d in st["deferred_detail"]:
        ws.cell(row=r, column=1, value=d["event_date"])
        ws.cell(row=r, column=2, value=d["invoice"])
        ws.cell(row=r, column=3, value=d["contact"])
        ws.cell(row=r, column=4, value=d["paid_date"])
        c = ws.cell(row=r, column=5, value=d["amount"]); c.number_format = M
        if r % 2 == 0:
            for col in range(1, 6):
                ws.cell(row=r, column=col).fill = BAND
        r += 1
    ws.cell(row=r, column=4, value="TOTAL").font = Font(bold=True)
    c = ws.cell(row=r, column=5, value=st["deferred_revenue"])
    c.number_format = M; c.font = Font(bold=True); c.fill = TOTAL

    # ───────────────────────── Depreciation ─────────────────────────
    ws = wb.create_sheet("Fleet & Depreciation")
    title(ws, "Rental Fleet and Depreciation", "Straight line. Fleet is capitalized, not expensed on purchase.")
    header(ws, 4, ["Placed in service", "Asset", "Account", "Cost", "Life (mo)", "Months held", "Depreciation", "Net book value"],
           [16, 42, 10, 13, 11, 13, 14, 15])
    r = 5
    for d in sorted(st["depreciation_schedule"], key=lambda x: x["date"]):
        ws.cell(row=r, column=1, value=d["date"]); ws.cell(row=r, column=2, value=d["asset"])
        ws.cell(row=r, column=3, value=d["code"])
        for col, key in ((4, "cost"), (7, "depreciation"), (8, "net_book_value")):
            c = ws.cell(row=r, column=col, value=d[key]); c.number_format = M
        ws.cell(row=r, column=5, value=d["life_months"]); ws.cell(row=r, column=6, value=d["months_held"])
        r += 1
    ws.cell(row=r, column=3, value="TOTAL").font = Font(bold=True)
    for col, val in ((4, st["fleet_cost"]), (7, st["accumulated_depreciation"]), (8, st["fleet_nbv"])):
        c = ws.cell(row=r, column=col, value=val); c.number_format = M; c.font = Font(bold=True); c.fill = TOTAL

    # ───────────────────────── Needs Review ─────────────────────────
    ws = wb.create_sheet("Needs Review")
    title(ws, "Transactions To Confirm",
          "My best guess is applied. Correct the Account column and the statements can be rebuilt.")
    header(ws, 4, ["Date", "Source", "Description", "Amount", "Account", "Why I flagged it"],
           [12, 22, 42, 13, 34, 52])
    r = 5
    for t in sorted([x for x in led if x["confidence"] == "review"], key=lambda x: -abs(x["amount"])):
        ws.cell(row=r, column=1, value=t["date"]); ws.cell(row=r, column=2, value=t["account"])
        ws.cell(row=r, column=3, value=t["description"][:60])
        c = ws.cell(row=r, column=4, value=t["amount"]); c.number_format = M
        ws.cell(row=r, column=5, value=f'{t["account_code"]} {names.get(t["account_code"],"")}')
        ws.cell(row=r, column=6, value=t["note"])
        if r % 2 == 0:
            for col in range(1, 7):
                ws.cell(row=r, column=col).fill = BAND
        r += 1

    # ───────────────────────── Transactions ─────────────────────────
    ws = wb.create_sheet("Transactions")
    title(ws, "All Transactions", "Every row from the three statements, coded. This is the source of every number above.")
    header(ws, 4, ["ID", "Date", "Source account", "Description", "Amount", "Code", "Account", "Confidence", "Note"],
           [8, 12, 22, 52, 13, 8, 34, 12, 48])
    r = 5
    for t in led:
        ws.cell(row=r, column=1, value=t["txn_id"]); ws.cell(row=r, column=2, value=t["date"])
        ws.cell(row=r, column=3, value=t["account"]); ws.cell(row=r, column=4, value=t["description"][:90])
        c = ws.cell(row=r, column=5, value=t["amount"]); c.number_format = M
        ws.cell(row=r, column=6, value=t["account_code"])
        ws.cell(row=r, column=7, value=names.get(t["account_code"], ""))
        cf = ws.cell(row=r, column=8, value=t["confidence"])
        if t["confidence"] == "review":
            cf.fill = WARN
        ws.cell(row=r, column=9, value=t["note"][:70])
        r += 1
    ws.auto_filter.ref = f"A4:I{r-1}"

    # ───────────────────────── Data Gaps ─────────────────────────
    ws = wb.create_sheet("Data Gaps")
    title(ws, "What I Could Not Verify", "Read this before presenting these numbers to anyone.")
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 96
    gaps = [
        ("Apple Card history", "The export covers 6/1/2026 onward only. April and May charges are missing, so the card's "
         "balance cannot be derived and the balance sheet does not close on its own. The gap is shown openly as "
         "'Opening balance equity / unreconciled' rather than hidden in a plug."),
        ("A fourth payment method", "A Sam's Club receipt dated 6/5/2026 was paid with an AMEX ending 1029 for $38.59. "
         "That card is not among the three statements provided, so any business spending on it is missing entirely."),
        ("$1,500 to Capital One", "Chase sent $1,500 to Capital One on 8/5/2026 with no matching credit on the Savor "
         "statement. Either a second Capital One card exists or a statement is incomplete. Parked in 'Ask My Accountant'."),
        ("Cards paid before Chase opened", "$3,357.41 of Capital One payments in April, May and early June came from "
         "outside the Chase account, which opened 5/21. Treated as owner capital, since the money came from you."),
        ("Sales tax collected", "HighLevel does not expose a tax field per invoice, so tax collected cannot be split out "
         "of revenue. Revenue is therefore recorded gross of sales tax. $926.67 of remittances to the Texas Comptroller "
         "were identified. Revenue is overstated by whatever tax is embedded in it."),
        ("Personal and business are mixed", "Both cards carry clear personal spending - pool chemicals and filters, "
         "nutrition, personal care, groceries. I routed what I could identify to Owner Draws so it stays out of the P&L, "
         "but only you can confirm each one. See the Needs Review tab."),
        ("Merchant fees are derived", "Processor payouts arrive net, so fees never appear as their own transaction. "
         f"The ${st['revenue']['merchant_fees_derived']:,.2f} shown is invoiced gross less net payout less in-transit "
         f"({st['revenue']['fee_rate_pct']}% of volume), not a figure read off a statement."),
        ("Revenue with no event date", f"${rev['undated_on_receipt']:,.2f} sits on invoices whose names lack a leading "
         "date, so it is recognized when received rather than when earned. Naming every invoice 'YYYY-MM-DD ...' fixes this."),
    ]
    r = 5
    for h, body in gaps:
        c = ws.cell(row=r, column=1, value=h); c.font = Font(bold=True, size=10, color="B45309")
        c.alignment = Alignment(vertical="top")
        b = ws.cell(row=r, column=2, value=body); b.alignment = Alignment(wrap_text=True, vertical="top")
        b.font = Font(size=10)
        ws.row_dimensions[r].height = 46
        r += 1

    # ───────────────────────── Chart of Accounts ─────────────────────────
    ws = wb.create_sheet("Chart of Accounts")
    title(ws, "Chart of Accounts", "Built for a party and event rental business")
    header(ws, 4, ["Code", "Account", "Type", "Subtype", "Statement", "Notes"], [8, 44, 12, 20, 16, 60])
    r = 5
    for a in coa:
        for i, k in enumerate(["code", "account", "type", "subtype", "statement", "notes"], 1):
            ws.cell(row=r, column=i, value=a[k])
        r += 1

    for sheet in wb.worksheets:
        sheet.sheet_view.showGridLines = False
    path = os.path.join(OUT, "EP_Fiesta_Books_2026.xlsx")
    wb.save(path)
    print("wrote", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
