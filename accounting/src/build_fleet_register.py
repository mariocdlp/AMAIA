"""Generate the rental fleet register: a sheet Mario fills in, with live depreciation.

Uploaded to Drive as CSV; Google Sheets evaluates the formulas on import, so the
depreciation columns compute themselves as rows are typed.
"""
import json, csv, os

BASE = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(BASE, "out")
NCOL = 20            # pad to column T so the reference block lands on the right
FIRST = 5            # first data row
LAST = 200           # formulas/totals cover through here

# One source of truth for useful lives. build_statements.py imports this.
CATEGORIES = [
    ("Tables & Chairs",             84, "1510"),
    ("Tents, Canopies & Staging",   60, "1520"),
    ("Linens & Soft Goods",         36, "1530"),
    ("Decor, Lighting & Specialty", 60, "1540"),
    ("Inflatables & Games",         60, "1550"),
    ("Vehicles & Trailers",         60, "1600"),
    ("Shop & Warehouse Equipment",  84, "1650"),
    ("Leasehold Improvements",     120, "1700"),
]
CODE_TO_CAT = {c: n for n, _, c in CATEGORIES}
LIVES = {c: m for _, m, c in CATEGORIES}

HEADERS = ["Item / description", "Category", "Qty", "Unit cost", "Total cost",
           "Purchase date", "Vendor", "Paid with", "Useful life (mo)",
           "Months in service", "Monthly depreciation", "Accumulated depreciation",
           "Net book value", "Status", "Notes"]


def row(r, item="", cat="", qty="", unit="", date="", vendor="", paid="", status="", notes=""):
    """One data row. Columns E and I-M are formulas Sheets evaluates on import."""
    return [
        item, cat, qty, unit,
        f"=IF(C{r}*D{r}=0,\"\",C{r}*D{r})",
        date, vendor, paid,
        f"=IFERROR(VLOOKUP(B{r},$R$4:$S$11,2,0),\"\")",
        f"=IF(F{r}=\"\",\"\",MAX(0,DATEDIF(F{r},TODAY(),\"M\")))",
        f"=IFERROR(E{r}/I{r},\"\")",
        f"=IF(E{r}=\"\",\"\",IFERROR(MIN(E{r},K{r}*J{r}),\"\"))",
        f"=IF(E{r}=\"\",\"\",IFERROR(E{r}-L{r},\"\"))",
        status, notes,
    ]


def pad(cells):
    return cells + [""] * (NCOL - len(cells))


def main():
    led = json.load(open(os.path.join(OUT, "ledger_coded.json")))
    # categorize.py overwrites "account" with the COA name, so recover the source
    # bank/card account from the raw ledger by txn_id.
    source = {t["txn_id"]: t["account"] for t in json.load(open(os.path.join(OUT, "ledger_raw.json")))}
    fleet_codes = set(LIVES)

    known = sorted([t for t in led if t["account_code"] in fleet_codes], key=lambda t: t["date"])
    cand = sorted([t for t in led if t["amount"] <= -100
                   and t["account_code"] in {"5080", "5070", "5050", "6990"}
                   and "CAPITAL ONE" not in t["description"].upper()],
                  key=lambda t: t["amount"])

    src = {"Capital One Savor 5198": "Capital One Savor", "Apple Card": "Apple Card",
           "Chase Checking 5784": "Chase Checking"}

    out, r = [], FIRST
    for t in known:
        out.append(row(r, item=t["note"].split(" - ")[0][:58] or t["description"][:58],
                       cat=CODE_TO_CAT[t["account_code"]], qty=1, unit=round(-t["amount"], 2),
                       date=t["date"], vendor=t["description"][:28],
                       paid=src.get(source[t["txn_id"]], source[t["txn_id"]]), status="In service",
                       notes="Identified from statements - correct the description if wrong"))
        r += 1
    for t in cand:
        out.append(row(r, item="", cat="", qty=1, unit=round(-t["amount"], 2),
                       date=t["date"], vendor=t["description"][:28],
                       paid=src.get(source[t["txn_id"]], source[t["txn_id"]]), status="CONFIRM",
                       notes="Purchase I could not identify - name it and pick a category, or delete the row"))
        r += 1
    blanks = 45
    for _ in range(blanks):
        out.append(row(r)); r += 1
    last = r - 1

    path = os.path.join(OUT, "fleet_register.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(pad(["RENTAL FLEET REGISTER - El Paso Fiesta Tent & Party Rental"]))
        w.writerow(pad([
            "Type one row per item or per purchase. Fill columns A-H only; the grey columns "
            "(I-M) calculate themselves. Category must match the reference list on the right.",
            "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "",
            "CATEGORY REFERENCE", "", ""]))
        w.writerow(pad([
            "TOTALS", "", "", "",
            f"=SUM(E{FIRST}:E{LAST})", "", "", "", "", "",
            f"=SUM(K{FIRST}:K{LAST})", f"=SUM(L{FIRST}:L{LAST})", f"=SUM(M{FIRST}:M{LAST})",
            "", "", "", "Category", "Useful life (mo)", "Account"]))
        hdr = pad(HEADERS)
        hdr[17], hdr[18], hdr[19] = CATEGORIES[0][0], CATEGORIES[0][1], CATEGORIES[0][2]
        w.writerow(hdr)
        for i, cells in enumerate(out):
            c = pad(cells)
            if i + 1 < len(CATEGORIES):                      # reference rows 5..11
                n, m, code = CATEGORIES[i + 1]
                c[17], c[18], c[19] = n, m, code
            w.writerow(c)

    print(f"wrote {path}  ({os.path.getsize(path)} bytes)")
    print(f"  {len(known)} identified fleet rows, {len(cand)} to confirm, {blanks} blank")
    print(f"  data rows {FIRST}-{last}")


if __name__ == "__main__":
    main()
