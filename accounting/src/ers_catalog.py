"""Product catalog exported from ERS (Event Rental Systems), parsed by hand.

The export gives a PER-UNIT purchase price, not total spend, so quantity is
required before any of this can be valued or depreciated. Labor/COGS are
per-order operating figures ERS uses for pricing, not part of the asset cost.

Fields: (ers_category, item, unit_price or None, labor_per_order, coa_code)
coa_code None means the line is a service, not a fleet asset.
"""

# ERS category -> chart-of-accounts fleet code
CATEGORY_MAP = {
    "Canopy Tent Extras":    "1520",
    "Chairs":                "1510",
    "Decor":                 "1540",
    "Extras":                "1540",
    "Hidden Category":       None,      # services, not assets
    "High Peak Tent Extras": "1520",
    "Tablecloths":           "1530",
    "Tables":                "1510",
    "Tents":                 "1520",
}

CATALOG = [
    ("Canopy Tent Extras", "Staking Kit for Canopy Tent",                  55.00, 0.00),
    ("Canopy Tent Extras", "String Lights 10x10 Tent",                     34.00, 0.00),
    ("Canopy Tent Extras", "String Lights 10x20 Tent",                     68.00, 0.00),
    ("Canopy Tent Extras", "Walls and Windows Kit for 10x10 Canopy",       20.00, 0.00),
    ("Canopy Tent Extras", "Walls and Windows Kit for 10x20 Canopy",       40.00, 0.00),
    ("Chairs",             "Kids Table with 4 Chairs",                     80.00, 1.00),
    ("Chairs",             "Padded White Garden Chairs",                   27.50, 0.33),
    ("Chairs",             "Party Chairs",                                 13.00, 0.33),
    ("Decor",              "Backdrop Arches and Pedestals",                60.00, 1.00),
    ("Decor",              "Custom Backdrop Arches & Pedestals Set",      125.00, 5.00),
    ("Decor",              "Red Rose Heart Arch",                          None, 0.00),
    ("Extras",             "3-Speed Porta Cooler",                         None, 0.00),
    ("Extras",             "Monster Z6 Party Speaker",                     None, 0.00),
    ("Hidden Category",    "Canopy Installation",                          None, 0.25),
    ("Hidden Category",    "Setup and Tear Down",                          None, 0.25),
    ("High Peak Tent Extras", "20x20 High Peak Tent Draping",             625.00, 0.00),
    ("High Peak Tent Extras", "Ballasting equipment",                     100.00, 0.00),
    ("High Peak Tent Extras", "High Peak Tent Walls - 20ft",              250.00, 0.00),
    ("High Peak Tent Extras", "High Peak Tent Windows - 20 ft",           450.00, 0.00),
    ("High Peak Tent Extras", "String Lights 10x10 tent",                  34.00, 0.00),
    ("High Peak Tent Extras", "String Lights 20x20 Tent",                 136.00, 0.00),
    ("Tablecloths",        "Wind-Proof Tablecloth for 5 ft Round Table",   None, 0.00),
    ("Tablecloths",        '36" Spandex Fitted Cocktail Table Cover',      None, 0.00),
    ("Tablecloths",        "Round Tablecloth for 5ft round table - White", 13.00, 7.00),
    ("Tablecloths",        "Spandex Tablecloth 6 ft - White",               9.00, 2.00),
    ("Tablecloths",        "Table Runners - Black",                         3.00, 2.00),
    ("Tablecloths",        "Table Runners - White",                         3.00, 2.00),
    ("Tables",             "42'' Cocktail Table",                          None, 0.00),
    ("Tables",             "5ft Round Table",                              99.00, 0.00),
    ("Tables",             "6ft Rectangle Serving (slim) Table",          120.00, 0.00),
    ("Tables",             "6ft Rectangle Table",                          72.00, 0.00),
    ("Tables",             "8ft Rectangle Table",                         100.00, 0.00),
    ("Tents",              "10x10 Canopy Tent",                           239.00, 20.00),
    ("Tents",              "10x20 Canopy Tent",                           448.00, 30.00),
    ("Tents",              "20x20 High Peak Tent",                       2300.00, 80.00),
]

# Same physical product listed under two ERS categories - count the units once.
DUPLICATES = {("High Peak Tent Extras", "String Lights 10x10 tent"):
              "Same item as 'String Lights 10x10 Tent' under Canopy Tent Extras"}


def assets():
    """Catalog lines that are fleet assets (excludes services)."""
    return [(c, n, p, l) for c, n, p, l in CATALOG if CATEGORY_MAP[c]]


def services():
    return [(c, n, p, l) for c, n, p, l in CATALOG if not CATEGORY_MAP[c]]


if __name__ == "__main__":
    a, s = assets(), services()
    priced = [x for x in a if x[2] is not None]
    missing = [x for x in a if x[2] is None]
    print(f"{len(CATALOG)} catalog lines: {len(a)} assets, {len(s)} services")
    print(f"  priced {len(priced)}, missing a price {len(missing)}")
    print(f"  one of each priced item = ${sum(x[2] for x in priced):,.2f}")
    print(f"  duplicate listings: {len(DUPLICATES)}")
    print("\nMISSING A PURCHASE PRICE:")
    for c, n, p, l in missing:
        print(f"  {c:24s} {n}")
    print("\nSERVICES (not fleet):")
    for c, n, p, l in s:
        print(f"  {n:28s} labor/order ${l:.2f}")
    print("\nBY COA CATEGORY:")
    import collections
    agg = collections.defaultdict(lambda: [0, 0.0])
    for c, n, p, l in a:
        agg[CATEGORY_MAP[c]][0] += 1
        agg[CATEGORY_MAP[c]][1] += p or 0
    for code in sorted(agg):
        n, tot = agg[code]
        print(f"  {code}  {n:2d} item types, ${tot:>8,.2f} for one of each")
