"""Compute the three statements plus reconciliation, on a cash basis with deposit tracking."""
import json, csv, os, datetime, collections

BASE = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(BASE, "out")
PERIOD_START = datetime.date(2026, 4, 1)
PERIOD_END = datetime.date(2026, 9, 18)

# Useful lives in months, by account code.
LIVES = {"1510": 60, "1520": 60, "1530": 36, "1540": 60, "1550": 60,
         "1600": 60, "1650": 84, "1700": 60}


def load():
    led = json.load(open(os.path.join(OUT, "ledger_coded.json")))
    ghl = json.load(open(os.path.join(OUT, "ghl_payments.json")))
    coa = {r["code"]: r for r in csv.DictReader(open(os.path.join(BASE, "chart_of_accounts.csv")))}
    return led, ghl, coa


def revenue_recognition(ghl):
    earned, deferred, undated = [], [], []
    for r in ghl:
        if not r["event_date"]:
            undated.append(r)
        elif datetime.date.fromisoformat(r["event_date"]) > PERIOD_END:
            deferred.append(r)
        else:
            earned.append(r)
    return earned, deferred, undated


def depreciation(led):
    """Straight line, monthly, starting the month after the asset is placed in service."""
    rows, total = [], 0.0
    for t in led:
        life = LIVES.get(t["account_code"])
        if not life or t["amount"] >= 0:
            continue
        cost = -t["amount"]
        d = datetime.date.fromisoformat(t["date"])
        months = (PERIOD_END.year - d.year) * 12 + (PERIOD_END.month - d.month)
        months = max(0, months)
        dep = round(min(cost, cost / life * months), 2)
        total += dep
        rows.append({"date": t["date"], "asset": t["description"][:40], "code": t["account_code"],
                     "cost": cost, "life_months": life, "months_held": months, "depreciation": dep,
                     "net_book_value": round(cost - dep, 2)})
    return rows, round(total, 2)


def main():
    led, ghl, coa = load()
    earned, deferred, undated = revenue_recognition(ghl)

    rev_earned = round(sum(r["amount"] for r in earned), 2)
    rev_undated = round(sum(r["amount"] for r in undated), 2)
    rev_recognized = round(rev_earned + rev_undated, 2)
    rev_deferred = round(sum(r["amount"] for r in deferred), 2)
    ghl_gross = round(rev_recognized + rev_deferred, 2)

    # cash actually received from customers, per the bank
    bank_customer = round(sum(t["amount"] for t in led if t["account_code"] == "4010"), 2)
    # GHL payments taken while the Chase account existed
    ghl_since_bank = round(sum(r["amount"] for r in ghl if r["paid_date"] >= "2026-05-21"), 2)
    # Processor payouts settle ~2 business days behind the charge, so the most recent
    # charges are still in transit at period end and belong on the balance sheet.
    in_transit = round(sum(r["amount"] for r in ghl if r["paid_date"] >= "2026-09-15"), 2)
    merchant_fees = round(ghl_since_bank - bank_customer - in_transit, 2)
    fee_rate = round(merchant_fees / ghl_since_bank * 100, 2) if ghl_since_bank else 0.0

    by = collections.defaultdict(float)
    for t in led:
        by[t["account_code"]] += t["amount"]

    dep_rows, dep_total = depreciation(led)

    def s(code):
        return round(-by.get(code, 0.0), 2)   # expense accounts: flip to positive

    cogs = {c: s(c) for c in ["5010", "5020", "5030", "5040", "5050", "5060", "5070", "5080", "5100"] if by.get(c)}
    cogs["5090"] = merchant_fees
    opex = {c: s(c) for c in sorted(by) if c.startswith("6") and by.get(c)}
    opex["6800"] = dep_total

    total_cogs = round(sum(cogs.values()), 2)
    total_opex = round(sum(opex.values()), 2)
    gross_profit = round(rev_recognized - total_cogs, 2)
    other_income = round(by.get("7020", 0.0), 2)
    net_income = round(gross_profit - total_opex + other_income, 2)

    # ---- balance sheet ------------------------------------------------------
    chase = [t for t in led if t["acct_type"] == "checking"]
    cash = round(sum(t["amount"] for t in chase), 2)   # Chase opened at 0 on 5/21
    fleet = {c: s(c) for c in ["1510", "1520", "1530", "1540", "1550", "1650"] if by.get(c)}
    fleet_cost = round(sum(fleet.values()), 2)

    # Card balances are only derivable where the export covers the card's whole life.
    raw = json.load(open(os.path.join(OUT, "ledger_raw.json")))
    card_bal = {}
    for name in {r["account"] for r in raw if r["acct_type"] == "credit_card"}:
        card_bal[name] = round(-sum(r["amount"] for r in raw if r["account"] == name), 2)

    owner_contrib = round(by.get("3010", 0.0), 2)
    owner_draws = round(-by.get("3020", 0.0), 2)

    out = {
        "period": {"start": PERIOD_START.isoformat(), "end": PERIOD_END.isoformat()},
        "revenue": {"earned_by_event": rev_earned, "undated_on_receipt": rev_undated,
                    "recognized": rev_recognized, "deferred": rev_deferred, "ghl_gross": ghl_gross,
                    "bank_received": bank_customer, "ghl_since_bank_open": ghl_since_bank,
                    "in_transit": in_transit, "merchant_fees_derived": merchant_fees,
                    "fee_rate_pct": fee_rate},
        "cogs": cogs, "total_cogs": total_cogs, "gross_profit": gross_profit,
        "opex": opex, "total_opex": total_opex,
        "other_income": other_income, "net_income": net_income,
        "cash_chase": cash, "undeposited_funds": in_transit,
        "card_balances": card_bal, "fleet": fleet, "fleet_cost": fleet_cost,
        "accumulated_depreciation": dep_total, "fleet_nbv": round(fleet_cost - dep_total, 2),
        "deferred_revenue": rev_deferred,
        "sales_tax_remitted": round(-by.get("2300", 0.0), 2),
        "owner_contributions": owner_contrib, "owner_draws": owner_draws,
        "uncategorized": round(-by.get("6990", 0.0), 2),
        "depreciation_schedule": dep_rows,
        "deferred_detail": sorted(deferred, key=lambda r: r["event_date"]),
    }
    json.dump(out, open(os.path.join(OUT, "statements.json"), "w"), indent=1)

    print(f"REVENUE recognized      {rev_recognized:>12,.2f}")
    print(f"  deferred (liability)  {rev_deferred:>12,.2f}")
    print(f"  in transit at 9/18    {in_transit:>12,.2f}")
    print(f"  merchant fees derived {merchant_fees:>12,.2f}  ({fee_rate:.2f}% of volume)")
    print(f"COGS                    {total_cogs:>12,.2f}")
    print(f"GROSS PROFIT            {gross_profit:>12,.2f}   ({gross_profit/rev_recognized*100:.1f}%)")
    print(f"OPEX                    {total_opex:>12,.2f}")
    print(f"Other income            {other_income:>12,.2f}")
    print(f"NET INCOME              {net_income:>12,.2f}")
    print(f"\nCash (Chase)            {cash:>12,.2f}")
    print(f"Fleet at cost           {fleet_cost:>12,.2f}")
    print(f"Accum depreciation      {dep_total:>12,.2f}")
    print(f"Owner contributions     {owner_contrib:>12,.2f}")
    print(f"Owner draws             {owner_draws:>12,.2f}")
    for k, v in card_bal.items():
        print(f"Card balance {k:<24s}{v:>10,.2f}")


if __name__ == "__main__":
    main()
