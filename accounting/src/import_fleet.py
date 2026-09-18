"""Read the filled-in fleet register and produce the depreciation schedule.

Export the Google Sheet as CSV (File > Download > CSV) into data_raw/fleet_register.csv,
then run this. Rows without a category, a cost or a date are skipped, so the blank
rows and any CONFIRM rows you never got to are simply ignored.
"""
import csv, json, os, sys, datetime
sys.path.insert(0, os.path.dirname(__file__))
from build_fleet_register import CATEGORIES

BASE = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(BASE, "data_raw", "fleet_register.csv")
OUT = os.path.join(BASE, "out")
PERIOD_END = datetime.date(2026, 9, 18)

CAT_LIFE = {n: m for n, m, _ in CATEGORIES}
CAT_CODE = {n: c for n, _, c in CATEGORIES}


def full_months(start, end):
    """Whole months elapsed - matches Google Sheets DATEDIF(start, end, "M")."""
    m = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day < start.day:
        m -= 1
    return max(0, m)


def money(s):
    s = (s or "").strip().replace("$", "").replace(",", "")
    try:
        return float(s)
    except ValueError:
        return 0.0


def main():
    if not os.path.exists(RAW):
        sys.exit(f"Put the exported register at {RAW} first.")
    rows, skipped = [], 0
    with open(RAW, encoding="utf-8-sig") as fh:
        for i, r in enumerate(csv.reader(fh), 1):
            if i <= 4 or len(r) < 7:          # title, instructions, totals, header
                continue
            item, cat, qty, unit, _total, date = (r[0].strip(), r[1].strip(), r[2],
                                                  r[3], r[4], r[5].strip())
            cost = money(unit) * (money(qty) or 1)
            if not cat or cat not in CAT_LIFE or cost <= 0 or not date:
                if any(c.strip() for c in r[:8]):
                    skipped += 1
                continue
            try:
                d = datetime.date.fromisoformat(date)
            except ValueError:
                skipped += 1
                continue
            life = CAT_LIFE[cat]
            months = full_months(d, PERIOD_END)
            dep = round(min(cost, cost / life * months), 2)
            rows.append({"date": date, "asset": item or "(unnamed)", "category": cat,
                         "code": CAT_CODE[cat], "cost": round(cost, 2),
                         "life_months": life, "months_held": months,
                         "depreciation": dep, "net_book_value": round(cost - dep, 2),
                         "vendor": r[6].strip(), "paid_with": r[7].strip() if len(r) > 7 else ""})

    rows.sort(key=lambda x: x["date"])
    json.dump(rows, open(os.path.join(OUT, "fleet.json"), "w"), indent=1)

    cost = round(sum(r["cost"] for r in rows), 2)
    dep = round(sum(r["depreciation"] for r in rows), 2)
    print(f"{len(rows)} fleet assets, {skipped} rows skipped (no category, cost or date)")
    print(f"  cost {cost:>12,.2f}\n  accumulated depreciation {dep:>12,.2f}\n  net book value {cost-dep:>12,.2f}")
    by = {}
    for r in rows:
        by.setdefault(r["code"], [0, 0.0])
        by[r["code"]][0] += 1
        by[r["code"]][1] += r["cost"]
    for code in sorted(by):
        n, amt = by[code]
        print(f"  {code}  {n:3d} items  {amt:>10,.2f}")


if __name__ == "__main__":
    main()
