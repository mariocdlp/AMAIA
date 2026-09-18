"""Generate the CSVs that become the native Google Sheets in Drive.

Drive converts a CSV to a one-tab Sheet, so the books are split by shape:
statements (narrow), transactions (wide), fleet register (editable formulas).
"""
import json, csv, os, sys

BASE = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(BASE, "out")


def load():
    st = json.load(open(os.path.join(OUT, "statements.json")))
    led = json.load(open(os.path.join(OUT, "ledger_coded.json")))
    raw = {t["txn_id"]: t["account"] for t in json.load(open(os.path.join(OUT, "ledger_raw.json")))}
    coa = {r["code"]: r["account"] for r in csv.DictReader(open(os.path.join(BASE, "chart_of_accounts.csv")))}
    return st, led, raw, coa


SHORT = {"Capital One Savor 5198": "Savor 5198", "Apple Card": "Apple Card",
         "Chase Checking 5784": "Chase 5784"}


def transactions(path):
    st, led, raw, coa = load()
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["ALL TRANSACTIONS - El Paso Fiesta"])
        w.writerow(["Column B is the bank or card it came from. Data > Create a filter to slice by bank."])
        w.writerow(["Date", "Bank / card", "Description", "Amount", "Code", "Account", "Flag"])
        for t in led:
            w.writerow([t["date"], SHORT.get(raw[t["txn_id"]], raw[t["txn_id"]]),
                        t["description"][:40], t["amount"], t["account_code"],
                        t["account"][:30], "REVIEW" if t["confidence"] == "review" else ""])


def statements(path):
    st, led, raw, coa = load()
    rev = st["revenue"]
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["EL PASO FIESTA TENT & PARTY RENTAL"])
        w.writerow([f"Inception (April 2026) through {st['period']['end']} - cash basis with deposit tracking"])
        w.writerow([])
        w.writerow(["WHICH ACCOUNT THE MONEY MOVED THROUGH", "Spent", "Received", "Transactions"])
        for acct in sorted({raw[t["txn_id"]] for t in led}):
            rows = [t for t in led if raw[t["txn_id"]] == acct and t["account_code"] != "9010"]
            w.writerow([acct,
                        round(-sum(t["amount"] for t in rows if t["amount"] < 0), 2),
                        round(sum(t["amount"] for t in rows if t["amount"] > 0), 2),
                        len(rows)])
        w.writerow([])
        w.writerow(["REVENUE & EXPENDITURE", "Amount", "Note"])
        w.writerow(["Rental & event revenue (events delivered)", rev["earned_by_event"], "Recognized on event date"])
        w.writerow(["Revenue on invoices with no event date", rev["undated_on_receipt"], "Recognized on receipt"])
        w.writerow(["Total revenue recognized", rev["recognized"], ""])
        for c, a in sorted(st["cogs"].items()):
            w.writerow(["  " + coa.get(c, c), -a, "Derived: invoiced less net payout" if c == "5090" else ""])
        w.writerow(["Total cost of delivering events", -st["total_cogs"], ""])
        w.writerow(["GROSS PROFIT", st["gross_profit"], f"{st['gross_profit']/rev['recognized']*100:.1f}% margin"])
        for c, a in sorted(st["opex"].items()):
            w.writerow(["  " + coa.get(c, c), -a, "Non-cash" if c == "6800" else ""])
        w.writerow(["Total operating expenses", -st["total_opex"], ""])
        w.writerow(["Other income", st["other_income"], "Card cash back and bank bonus"])
        w.writerow(["NET INCOME", st["net_income"], ""])
        w.writerow([])
        w.writerow(["BALANCE SHEET", "Amount", "Note"])
        w.writerow(["Cash - Chase checking 5784", st["cash_chase"], ""])
        w.writerow(["Undeposited funds in transit", st["undeposited_funds"], "Charges 9/15-9/17 not yet settled"])
        for c, a in sorted(st["fleet"].items()):
            w.writerow(["  " + coa.get(c, c), a, "Capitalized rental fleet"])
        w.writerow(["Less accumulated depreciation", -st["accumulated_depreciation"], ""])
        ta = round(st["cash_chase"] + st["undeposited_funds"] + st["fleet_nbv"], 2)
        w.writerow(["TOTAL ASSETS", ta, ""])
        sav = st["card_balances"].get("Capital One Savor 5198", 0)
        w.writerow(["Credit card - Capital One Savor 5198", sav, ""])
        w.writerow(["Credit card - Apple Card", 0, "NOT DERIVABLE - export starts 6/1"])
        w.writerow(["Customer deposits held", st["deferred_revenue"], "LIABILITY - events not yet delivered"])
        tl = round(sav + st["deferred_revenue"], 2)
        w.writerow(["TOTAL LIABILITIES", tl, "Understated by the Apple Card balance"])
        w.writerow(["Owner contributions", st["owner_contributions"], ""])
        w.writerow(["Owner draws", -st["owner_draws"], ""])
        w.writerow(["Net income for the period", st["net_income"], ""])
        eq = round(st["owner_contributions"] - st["owner_draws"] + st["net_income"], 2)
        w.writerow(["Opening balance equity / unreconciled", round(ta - tl - eq, 2),
                    "Gap from missing Apple Card history"])
        w.writerow([])
        w.writerow(["CASH FLOW", "Amount", ""])
        op_out = round(st["total_cogs"] - st["cogs"].get("5090", 0) + st["total_opex"] - st["opex"].get("6800", 0), 2)
        w.writerow(["Cash received from customers", rev["bank_received"], ""])
        w.writerow(["Cash paid for events and operations", -op_out, ""])
        w.writerow(["Sales tax remitted to Texas", -st["sales_tax_remitted"], ""])
        w.writerow(["Purchase of rental fleet", -st["fleet_cost"], "Investing"])
        w.writerow(["Owner contributions less draws", round(st["owner_contributions"] - st["owner_draws"], 2), "Financing"])
        w.writerow([])
        w.writerow(["CUSTOMER DEPOSITS HELD - events not yet delivered"])
        w.writerow(["Event date", "Amount", "Invoice"])
        for d in st["deferred_detail"]:
            w.writerow([d["event_date"], d["amount"], d["invoice"]])
        w.writerow(["TOTAL", st["deferred_revenue"], ""])
        w.writerow([])
        w.writerow(["WHAT I COULD NOT VERIFY"])
        for h, b in [
            ("Apple Card history", "Export covers 6/1/2026 onward only, so its balance is not derivable and the "
             "balance sheet does not close on its own. The gap is shown openly, not hidden in a plug."),
            ("A fourth payment method", "A Sam's Club receipt dated 6/5/2026 was paid with an AMEX ending 1029. "
             "That card is not among the three statements provided."),
            ("$1,500 to Capital One", "Chase sent $1,500 on 8/5/2026 with no matching Savor credit. Parked in 6990."),
            ("Cards paid before Chase opened", "$3,357.41 of Capital One payments came from outside Chase, which "
             "opened 5/21. Treated as owner capital."),
            ("Sales tax collected", "HighLevel exposes no per-invoice tax field, so revenue is gross of sales tax. "
             "$926.67 of remittances to the Texas Comptroller were identified."),
            ("Personal and business mixed", "Both cards carry personal spending. What I could identify went to Owner "
             "Draws; the rest is flagged REVIEW on the transactions sheet."),
            ("Merchant fees are derived", f"${rev['merchant_fees_derived']:,.2f} is invoiced gross less net payout "
             f"less in-transit ({rev['fee_rate_pct']}% of volume), not read off a statement."),
        ]:
            w.writerow([h, b])


if __name__ == "__main__":
    transactions(os.path.join(OUT, "transactions.csv"))
    statements(os.path.join(OUT, "statements.csv"))
    for f in ("transactions.csv", "statements.csv"):
        print(f, os.path.getsize(os.path.join(OUT, f)), "bytes")
