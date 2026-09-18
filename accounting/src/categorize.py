"""Apply rules to the raw ledger, match interaccount transfers, and emit a coded ledger."""
import json, csv, os, sys, datetime, collections
sys.path.insert(0, os.path.dirname(__file__))
import rules

BASE = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(BASE, "out")
PERIOD_END = datetime.date(2026, 9, 18)

coa = {}
with open(os.path.join(BASE, "chart_of_accounts.csv")) as fh:
    for r in csv.DictReader(fh):
        coa[r["code"]] = r


def main():
    led = json.load(open(os.path.join(OUT, "ledger_raw.json")))
    for t in led:
        acct, conf, note = rules.classify(t["description"], t["date"], t["amount"])
        t["account_code"] = acct
        t["account"] = coa.get(acct, {}).get("account", "UNKNOWN")
        t["confidence"] = conf
        t["note"] = note

    # --- match transfers between the three accounts -------------------------
    outs = [t for t in led if t["account_code"] == "9010" and t["amount"] < 0]
    ins = [t for t in led if t["account_code"] == "9010" and t["amount"] > 0]
    used = set()
    for o in outs:
        od = datetime.date.fromisoformat(o["date"])
        best = None
        for i in ins:
            if id(i) in used or abs(i["amount"] + o["amount"]) > 0.005:
                continue
            gap = abs((datetime.date.fromisoformat(i["date"]) - od).days)
            if gap <= 7 and (best is None or gap < best[0]):
                best = (gap, i)
        if best:
            used.add(id(best[1]))
            o["transfer_match"] = best[1]["txn_id"]
            best[1]["transfer_match"] = o["txn_id"]
    unmatched = [t for t in led if t["account_code"] == "9010" and "transfer_match" not in t]

    # An unmatched card PAYMENT received (positive, on a card) means the owner paid
    # the card from a personal source -> owner contribution, not an interaccount move.
    # An unmatched payment SENT from checking means it paid a card we have no
    # statement for -> park it for review rather than guessing.
    for t in unmatched:
        if t["amount"] > 0 and t["acct_type"] == "credit_card":
            t["account_code"], t["confidence"] = "3010", "review"
            t["note"] = "Card paid from a non-Chase source (Chase opened 5/21) - treated as owner capital"
        elif t["amount"] < 0 and t["acct_type"] == "checking":
            t["account_code"], t["confidence"] = "6990", "review"
            t["note"] = "Payment to a Capital One card with no matching statement credit - missing statement?"
        t["account"] = coa.get(t["account_code"], {}).get("account", "UNKNOWN")

    json.dump(led, open(os.path.join(OUT, "ledger_coded.json"), "w"), indent=1)

    # --- summaries -----------------------------------------------------------
    by = collections.defaultdict(float)
    for t in led:
        by[t["account_code"]] += t["amount"]

    print("=" * 72)
    print("CODED LEDGER BY ACCOUNT")
    print("=" * 72)
    for code in sorted(by):
        nm = coa.get(code, {}).get("account", "?")
        n = sum(1 for t in led if t["account_code"] == code)
        print(f"  {code}  {nm[:44]:<44} {by[code]:>12,.2f}  ({n})")

    rev = [t for t in led if t["confidence"] == "review"]
    print(f"\nNeeds review: {len(rev)} transactions, "
          f"${sum(abs(t['amount']) for t in rev):,.2f}")

    print(f"\nUNMATCHED TRANSFERS ({len(unmatched)}):")
    for t in unmatched:
        print(f"  {t['date']}  {t['amount']:>10,.2f}  {t['account_name'] if 'account_name' in t else ''} "
              f"{t['description'][:60]}")
    return led


if __name__ == "__main__":
    main()
