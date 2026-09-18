"""Load the ERS item export (data_raw/ers_items.tsv) as the fleet inventory.

ERS holds what the bank statements cannot: what each item IS and how many there
are. It is not a clean asset register, so three kinds of line are handled apart:

  Package  - a bundle of other items (e.g. "40 Guest High Peak Event"). It has no
             purchase price of its own; capitalizing it would double count the
             items inside it. Excluded.
  Variant  - a colour/size sub-listing. Six tablecloth variants each carry qty 20
             at $9.00. Whether those are separate physical stock or re-listings of
             the same stock cannot be told from the export, so they are excluded
             from the fleet total and reported separately for confirmation.
  Services - "Canopy Installation", "Setup and Tear Down". Labor, not equipment.

`cost` in the export is the RENTAL RATE charged, not a cost to us. `purchase_price`
is per unit and `cogs` is per-order labor.
"""
import csv, os

RAW = os.path.join(os.path.dirname(__file__), "..", "data_raw", "ers_items.tsv")

# ERS categoryid -> (label, chart-of-accounts fleet code). None = not a fleet asset.
CATEGORIES = {
    "2691": ("Tents",                 "1520"),
    "2705": ("High Peak Tent Extras", "1520"),
    "2706": ("Canopy Tent Extras",    "1520"),
    "2692": ("Tables",                "1510"),
    "2703": ("Chairs",                "1510"),
    "2704": ("Tablecloths",           "1530"),
    "2698": ("Decor",                 "1540"),
    "2702": ("Extras",                "1540"),
    "2679": ("Services",              None),
    "2697": ("Packages",              None),
}

# Same product name under two categories; qty may be separate stock or a re-listing.
AMBIGUOUS = {"string lights 10x10 tent"}


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def load():
    items = []
    with open(RAW, encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            name = (r.get("name") or "").strip()
            if not name or (r.get("_deleted") or "").strip() not in ("", "0"):
                continue
            label, code = CATEGORIES.get(r.get("categoryid", ""), ("Unknown", None))
            items.append({
                "name": name,
                "ers_category": label,
                "coa_code": code,
                "type": (r.get("type") or "Regular").strip(),
                "qty": _num(r.get("qty")) or 0,
                "unit_price": _num(r.get("purchase_price")),
                "labor_per_order": _num(r.get("cogs")) or 0.0,
                "rental_rate": _num(r.get("cost")),
                "date_acq": (r.get("date_acq") or "").strip(),
                "manufacturer": (r.get("manufacturer") or "").strip(),
            })
    return items


def fleet():
    """Regular, non-service lines - the ones that represent owned equipment."""
    return [i for i in load() if i["coa_code"] and i["type"] == "Regular"]


def variants():
    return [i for i in load() if i["coa_code"] and i["type"] == "Variant"]


def packages():
    return [i for i in load() if i["type"] == "Package"]


def services():
    return [i for i in load() if i["coa_code"] is None and i["type"] != "Package"]


def valued():
    return [i for i in fleet() if i["unit_price"] is not None and i["qty"]]


def unpriced():
    return [i for i in fleet() if i["unit_price"] is None]


def total_cost():
    return round(sum(i["unit_price"] * i["qty"] for i in valued()), 2)


if __name__ == "__main__":
    import collections
    f, v, p, s = fleet(), variants(), packages(), services()
    print(f"{len(load())} ERS lines -> {len(f)} fleet, {len(v)} variants, "
          f"{len(p)} packages, {len(s)} services")
    print(f"fleet at cost: ${total_cost():,.2f}  ({len(valued())} priced, {len(unpriced())} unpriced)")
    print(f"variants held back: {len(v)} lines, "
          f"${sum(i['unit_price']*i['qty'] for i in v if i['unit_price']):,.2f}")
    agg = collections.defaultdict(float)
    for i in valued():
        agg[i["coa_code"]] += i["unit_price"] * i["qty"]
    print("\nby COA code:")
    for c in sorted(agg):
        print(f"  {c}  {agg[c]:>12,.2f}")
    print("\nunpriced (qty known, cost unknown):")
    for i in unpriced():
        print(f"  {i['name'][:46]:<46} qty {i['qty']:>5.0f}  {i['ers_category']}")
    dated = [i for i in f if i["date_acq"]]
    print(f"\nacquisition dates present on {len(dated)} of {len(f)} fleet lines:")
    for i in dated:
        print(f"  {i['name'][:46]:<46} {i['date_acq']}")
