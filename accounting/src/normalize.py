"""Normalize the three bank/card exports into one unified transaction ledger.

Sign convention: amount < 0 means money left the business (spend / card charge),
amount > 0 means money came in (deposit, refund, card payment credit).
"""
import csv, re, os, json

RAW = os.path.join(os.path.dirname(__file__), "..", "data_raw")
OUT = os.path.join(os.path.dirname(__file__), "..", "out")


def money(s):
    s = (s or "").strip().replace("$", "").replace(",", "")
    if not s:
        return 0.0
    return float(s)


def clean(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def load_savor():
    """Capital One Savor card ...5198. Latin-1, Spanish headers, Debito/Credito split."""
    rows = []
    with open(os.path.join(RAW, "savor.csv"), encoding="latin-1") as fh:
        for i, r in enumerate(csv.reader(fh)):
            if i == 0 or len(r) < 7 or not r[0].strip():
                continue
            debit, credit = money(r[5]), money(r[6])
            rows.append({
                "date": r[0].strip(),
                "account": "Capital One Savor 5198",
                "acct_type": "credit_card",
                "description": clean(r[3]),
                "bank_category": clean(r[4]),
                "amount": round(credit - debit, 2),
            })
    return rows


def load_apple():
    """Apple Card. Amount positive = purchase, negative = payment received."""
    rows = []
    with open(os.path.join(RAW, "applecard.csv"), encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            if not r.get("Transaction Date"):
                continue
            m, d, y = r["Transaction Date"].split("/")
            rows.append({
                "date": f"{y}-{m}-{d}",
                "account": "Apple Card",
                "acct_type": "credit_card",
                "description": clean(r.get("Merchant") or r.get("Description")),
                "bank_category": clean(r.get("Category")),
                "amount": round(-money(r["Amount (USD)"]), 2),
                "raw_description": clean(r.get("Description")),
            })
    return rows


def load_chase():
    """Chase business checking ...5784. Amount already signed."""
    rows = []
    with open(os.path.join(RAW, "chase.csv"), encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            if not r.get("Posting Date"):
                continue
            m, d, y = r["Posting Date"].split("/")
            rows.append({
                "date": f"{y}-{m}-{d}",
                "account": "Chase Checking 5784",
                "acct_type": "checking",
                "description": clean(r["Description"]),
                "bank_category": clean(r.get("Type")),
                "amount": round(money(r["Amount"]), 2),
                "balance": r.get("Balance", "").strip(),
            })
    return rows


def main():
    rows = load_savor() + load_apple() + load_chase()
    rows.sort(key=lambda x: (x["date"], x["account"]))
    for n, r in enumerate(rows, 1):
        r["txn_id"] = f"T{n:04d}"
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "ledger_raw.json"), "w") as fh:
        json.dump(rows, fh, indent=1)

    print(f"{len(rows)} transactions")
    for acct in sorted({r["account"] for r in rows}):
        sub = [r for r in rows if r["account"] == acct]
        inflow = sum(r["amount"] for r in sub if r["amount"] > 0)
        outflow = sum(r["amount"] for r in sub if r["amount"] < 0)
        print(f"  {acct:26s} {len(sub):4d} txns  {sub[0]['date']} -> {sub[-1]['date']}"
              f"   in {inflow:>10,.2f}  out {outflow:>11,.2f}")


if __name__ == "__main__":
    main()
