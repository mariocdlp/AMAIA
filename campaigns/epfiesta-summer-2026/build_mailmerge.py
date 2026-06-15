"""
Build the EP Fiesta Summer 2026 mail-merge dataset and verify that every
group has >=25 deliverable contacts (rows with a physical street address).

Rules:
  - Drop any row without a `street` (this is direct mail, address is required)
  - Map every source category to a GROUP_KEY (see GROUPS below)
  - GROUP_KEY -> distinct letter file in letters/<group_key>.md
  - Any group landing below 25 contacts after filtering gets merged into the
    nearest sibling group, recorded in MERGE_FALLBACK
"""

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
SOURCE = HERE / "source" / "contacts_raw.csv"
OUT_MERGE = HERE / "mailmerge_contacts.csv"
OUT_EXCLUDED = HERE / "excluded_contacts.csv"
OUT_CATMAP = HERE / "category_map.csv"
OUT_GROUPS = HERE / "group_counts.csv"


# ---------------------------------------------------------------------------
# Source category -> group key. Every category that should receive a letter
# maps to one of the 15 group keys below. Categories pointing to None are
# dropped (admin offices, libraries, building names, etc.).
# ---------------------------------------------------------------------------

CATEGORY_TO_GROUP = {
    # ---- Catholic (church + Catholic schools + parish) ----
    "Catholic church":              "catholic",
    "Catholic school":              "catholic",
    "Parish":                       "catholic",

    # ---- Baptist ----
    "Baptist church":               "baptist",

    # ---- Pentecostal / Apostolic / Charismatic / Hispanic ----
    "Pentecostal church":           "pentecostal",
    "Apostolic church":             "pentecostal",
    "Assemblies of God church":     "pentecostal",
    "Foursquare church":            "pentecostal",
    "Hispanic church":              "pentecostal",

    # ---- Mainline Protestant ----
    "Methodist church":             "mainline_protestant",
    "United Methodist church":      "mainline_protestant",
    "Lutheran church":              "mainline_protestant",
    "Presbyterian church":          "mainline_protestant",
    "Episcopal church":             "mainline_protestant",
    "Anglican church":              "mainline_protestant",
    "Church of the Nazarene":       "mainline_protestant",
    "Church of Christ":             "mainline_protestant",
    "Disciples of Christ Church":   "mainline_protestant",
    "United Church of Christ":      "mainline_protestant",
    "Greek Orthodox church":        "mainline_protestant",
    "Eastern Orthodox Church":      "mainline_protestant",
    "Protestant church":            "mainline_protestant",
    "Church of Jesus Christ of Latter-day Saints": "mainline_protestant",

    # ---- Evangelical / Non-denominational / Christian church ----
    "Christian church":             "evangelical",
    "Non-denominational church":    "evangelical",
    "Evangelical church":           "evangelical",
    "Calvary Chapel church":        "evangelical",
    "Seventh-day Adventist church": "evangelical",
    "Gospel church":                "evangelical",
    "Korean church":                "evangelical",
    "Unity church":                 "evangelical",
    "Unitarian Universalist Church":"evangelical",

    # ---- Generic / non-denominational church + non-Christian places of worship ----
    "Church":                       "generic_church",
    "Religious institution":        "generic_church",
    "Religious organization":       "generic_church",
    "Religious destination":        "generic_church",
    "Religious goods store":        "generic_church",
    "Synagogue":                    "generic_church",
    "Orthodox synagogue":           "generic_church",
    "Conservative synagogue":       "generic_church",
    "Messianic synagogue":          "generic_church",
    "Hindu temple":                 "generic_church",
    "Buddhist temple":              "generic_church",
    "Parsi temple":                 "generic_church",
    "Shrine":                       "generic_church",
    "Mosque":                       "generic_church",

    # ---- Elementary & K-8 generalist ----
    "Elementary school":            "elementary",
    "Primary school":               "elementary",
    "Kindergarten":                 "elementary",
    "K-12 school":                  "elementary",
    "School":                       "elementary",
    "School house":                 "elementary",
    "Special education school":     "elementary",
    "General education school":     "elementary",
    "Bilingual school":             "elementary",
    "After school program":         "elementary",
    "Educational institution":      "elementary",
    "Public educational institution":"elementary",

    # ---- Middle school ----
    "Middle school":                "middle_school",

    # ---- High school & specialized HS ----
    "High school":                  "high_school",
    "Girls' high school":           "high_school",
    "Preparatory school":           "high_school",
    "Co-ed school":                 "high_school",
    "Gymnasium school":             "high_school",
    "Military school":              "high_school",
    "International school":         "high_school",

    # ---- Preschool & Montessori ----
    "Preschool":                    "preschool",
    "Montessori school":            "preschool",
    "Montessori preschool":         "preschool",

    # ---- Private / Charter / Religious K-12 ----
    "Private educational institution":"private_k12",
    "Religious school":             "private_k12",
    "Charter school":               "private_k12",

    # ---- Higher Ed (University, College, Research) ----
    "University":                   "higher_ed",
    "Public university":            "higher_ed",
    "College":                      "higher_ed",
    "Community college":            "higher_ed",
    "Christian college":            "higher_ed",
    "Graduate school":              "higher_ed",
    "Institute of technology":      "higher_ed",
    "Research institute":           "higher_ed",

    # ---- Vocational / Trade / Specialty / Beauty / Medical / Emergency ----
    "Trade school":                 "vocational",
    "Vocational school":            "vocational",
    "Technical school":             "vocational",
    "Beauty school":                "vocational",
    "Barber school":                "vocational",
    "Nursing school":               "vocational",
    "Medical school":               "vocational",
    "Dental school":                "vocational",
    "Massage school":               "vocational",
    "Culinary school":              "vocational",
    "Cooking school":               "vocational",
    "Bartending school":            "vocational",
    "Computer training school":     "vocational",
    "Language school":              "vocational",
    "English language school":      "vocational",
    "Aviation training institute":  "vocational",
    "Art school":                   "vocational",
    "Architecture school":          "vocational",
    "Engineering school":           "vocational",
    "Handicraft school":            "vocational",
    "Driving school":               "vocational",
    "Truck driving school":         "vocational",
    "Flight school":                "vocational",
    "Adult education school":       "vocational",
    "Emergency training school":    "vocational",
    "Fire fighters academy":        "vocational",
    "Police academy":               "vocational",
    "Firearms academy":             "vocational",

    # ---- Martial arts & combat sports ----
    "Martial arts school":          "martial_arts",
    "Karate school":                "martial_arts",
    "Taekwondo school":             "martial_arts",
    "Jujitsu school":               "martial_arts",
    "Self defense school":          "martial_arts",
    "Tai chi school":               "martial_arts",
    "Wrestling school":             "martial_arts",
    "Sports school":                "martial_arts",
    "Horse riding school":          "martial_arts",

    # ---- Dance, Ballet, Music ----
    "Dance school":                 "dance_music",
    "Ballet school":                "dance_music",
    "Music school":                 "dance_music",

    # ---- Dropped: admin / building / one-off / off-topic ----
    "School bus service":           None,
    "School administration office": None,
    "University library":           None,
    "University hospital":          None,
    "School district office":       None,
    "School center":                None,
    "Association / Organization":   None,
    "University lab room":          None,  # not in main map -> drop
    "Real estate school":           "vocational",
    "Mathematics school":           "vocational",
}


# The 15 groups -> human label, used in stats and as letter filenames
GROUPS = [
    "catholic",
    "baptist",
    "pentecostal",
    "mainline_protestant",
    "evangelical",
    "generic_church",
    "elementary",
    "middle_school",
    "high_school",
    "preschool",
    "private_k12",
    "higher_ed",
    "vocational",
    "martial_arts",
    "dance_music",
]

# If any group ends up < 25 after address-filtering, merge it into the
# fallback group listed here (chosen for closest event-type similarity).
MERGE_FALLBACK = {
    "pentecostal":  "generic_church",
    "middle_school":"elementary",
    "private_k12":  "elementary",
    "preschool":    "elementary",
    "dance_music":  "vocational",
}


def normalize(s):
    return (s or "").strip()


def has_address(row):
    street = normalize(row.get("street"))
    if not street:
        return False
    # Drop sentinel weird values we observed (single numbers, building names
    # used as street, etc.). Address must contain at least one letter and one
    # digit OR contain a comma+number pattern. Loose filter.
    if not any(c.isdigit() for c in street):
        return False
    return True


def main():
    rows_total = 0
    after_address = 0
    excluded = []
    by_group = defaultdict(list)
    seen_categories = Counter()
    unknown_categories = Counter()

    with SOURCE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows_total += 1
            title = normalize(row.get("title"))
            if not title:
                continue
            category = normalize(row.get("categories/0"))
            seen_categories[category] += 1

            base = {
                "title": title,
                "street": normalize(row.get("street")),
                "city": normalize(row.get("city")) or "El Paso",
                "state": normalize(row.get("state")) or "Texas",
                "phone": normalize(row.get("phone")),
                "website": normalize(row.get("website")),
                "category": category,
            }

            if not has_address(base):
                base["exclude_reason"] = "no_physical_address"
                excluded.append(base)
                continue
            after_address += 1

            if category not in CATEGORY_TO_GROUP:
                unknown_categories[category] += 1
                base["exclude_reason"] = f"unmapped_category:{category}"
                excluded.append(base)
                continue

            group = CATEGORY_TO_GROUP[category]
            if group is None:
                base["exclude_reason"] = f"dropped_category:{category}"
                excluded.append(base)
                continue

            base["group_key"] = group
            by_group[group].append(base)

    # Apply MERGE_FALLBACK for any small group ------------------------------
    for g in list(by_group.keys()):
        n = len(by_group[g])
        if n < 25 and g in MERGE_FALLBACK:
            target = MERGE_FALLBACK[g]
            print(f"  merging '{g}' ({n}) into '{target}' (was {len(by_group[target])})")
            for r in by_group[g]:
                r["group_key"] = target
                by_group[target].append(r)
            del by_group[g]

    # Write mail merge CSV --------------------------------------------------
    merged_rows = []
    for g in GROUPS:
        merged_rows.extend(by_group.get(g, []))

    merge_fields = ["title", "street", "city", "state", "phone", "website",
                    "category", "group_key"]
    with OUT_MERGE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=merge_fields)
        w.writeheader()
        for r in merged_rows:
            w.writerow({k: r.get(k, "") for k in merge_fields})

    # Excluded list ---------------------------------------------------------
    excluded_fields = ["title", "street", "city", "category", "exclude_reason",
                       "phone", "website"]
    with OUT_EXCLUDED.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=excluded_fields)
        w.writeheader()
        for r in excluded:
            w.writerow({k: r.get(k, "") for k in excluded_fields})

    # Group counts ---------------------------------------------------------
    with OUT_GROUPS.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["group_key", "count_deliverable"])
        for g in GROUPS:
            w.writerow([g, len(by_group.get(g, []))])

    # Category map ---------------------------------------------------------
    with OUT_CATMAP.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["category", "count_in_source", "group_key_assigned"])
        for cat, n in sorted(seen_categories.items(), key=lambda kv: -kv[1]):
            g = CATEGORY_TO_GROUP.get(cat, "UNKNOWN")
            # Account for fallback merges
            if g in MERGE_FALLBACK and g not in by_group:
                g = MERGE_FALLBACK[g]
            w.writerow([cat, n, g if g is not None else "DROPPED"])

    # Summary --------------------------------------------------------------
    print()
    print(f"Source rows scanned:    {rows_total}")
    print(f"  with valid address:   {after_address}")
    print(f"  excluded:             {len(excluded)}")
    print(f"  mail-merge ready:     {len(merged_rows)}")
    print()
    print("Group sizes (deliverable):")
    for g in GROUPS:
        n = len(by_group.get(g, []))
        flag = "  OK" if n >= 25 else "  <25 -- needs further merge"
        print(f"  {g:<22} {n:>4} {flag}")

    if unknown_categories:
        print()
        print("Unknown categories (left out, please review):")
        for c, n in unknown_categories.most_common():
            print(f"  {c}: {n}")


if __name__ == "__main__":
    main()
