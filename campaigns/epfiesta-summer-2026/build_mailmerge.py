"""
Build a mail-merge-ready dataset and bilingual letter template for EP Fiesta's
Summer 2026 outreach to El Paso churches and schools.

Input: source CSV exported from Google Maps scrape (col J = categories/0)
Output:
  - mailmerge_contacts.csv  -> one row per ready-to-send contact
  - excluded_contacts.csv   -> rows skipped (with reason)
  - category_map.csv        -> reference of every category and its EN/ES pitch
"""

import csv
import os
import sys
from pathlib import Path

HERE = Path(__file__).parent
SOURCE = HERE / "source" / "contacts_raw.csv"
OUT_MERGE = HERE / "mailmerge_contacts.csv"
OUT_EXCLUDED = HERE / "excluded_contacts.csv"
OUT_CATMAP = HERE / "category_map.csv"


# ---------------------------------------------------------------------------
# Category -> (use_case_en, use_case_es, segment)
# segment groups the kind of letter framing (church / school_k12 / higher_ed /
# vocational / other). One LETTER VARIANT per category is rendered via the
# use_case fields; segment is kept as a sanity-check label.
# ---------------------------------------------------------------------------

# Hispanic-church use cases lean into kermes / bautizos / aniversarios because
# those are the events where shade/tents are bought, not just nice-to-have.
CHURCH_GENERIC_EN = "your summer festivals, outdoor services and family gatherings"
CHURCH_GENERIC_ES = "los festivales de verano, servicios al aire libre y convivencias familiares"

CATHOLIC_EN = "your parish kermés, first communions, confirmaciones and outdoor masses"
CATHOLIC_ES = "la kermés parroquial, primeras comuniones, confirmaciones y misas al aire libre"

BAPTIST_EN = "your Vacation Bible School, summer revivals, homecomings and outdoor baptisms"
BAPTIST_ES = "la Escuela Bíblica de Vacaciones, campañas de verano, aniversarios y bautizos al aire libre"

HISPANIC_CHURCH_EN = "your kermés, conferencias, aniversarios and bautizos"
HISPANIC_CHURCH_ES = "la kermés, conferencias, aniversarios y bautizos"

NONDENOM_EN = "your outreach events, summer worship nights and family fun days"
NONDENOM_ES = "los eventos de alcance, noches de adoración al aire libre y días familiares"

JEWISH_EN = "your outdoor services, Sukkot gatherings and community celebrations"
JEWISH_ES = "los servicios al aire libre, celebraciones de Sukkot y eventos comunitarios"

EASTERN_TEMPLE_EN = "your cultural festivals, holiday celebrations and community pujas"
EASTERN_TEMPLE_ES = "los festivales culturales, celebraciones de festividades y eventos comunitarios"

MOSQUE_EN = "your Eid celebrations, community iftars and outdoor gatherings"
MOSQUE_ES = "las celebraciones de Eid, iftares comunitarios y eventos al aire libre"

# Schools — back-to-school + field day + graduation pitch
ELEM_EN = "your field day, fall carnival, back-to-school night and end-of-year celebration"
ELEM_ES = "el field day, el carnaval de otoño, la noche de regreso a clases y la celebración de fin de año"

MIDDLE_EN = "your back-to-school night, fall festival, dances and sports tournaments"
MIDDLE_ES = "la noche de regreso a clases, festival de otoño, bailes y torneos deportivos"

HIGH_EN = "your graduation, homecoming, prom afterparties and outdoor sports tournaments"
HIGH_ES = "la graduación, homecoming, after-party de prom y torneos deportivos al aire libre"

PRESCHOOL_EN = "your family days, parent appreciation events and Pre-K graduation"
PRESCHOOL_ES = "los días familiares, eventos de agradecimiento a padres y la graduación de Pre-K"

CHARTER_EN = "your back-to-school events, family nights and end-of-year celebrations"
CHARTER_ES = "los eventos de regreso a clases, noches familiares y celebraciones de fin de año"

MONTESSORI_EN = "your outdoor learning days, family picnics and community open houses"
MONTESSORI_ES = "los días de aprendizaje al aire libre, días de campo familiares y open houses comunitarios"

PRIVATE_K12_EN = "your open houses, fundraising galas, family days and graduations"
PRIVATE_K12_ES = "los open houses, galas de recaudación, días familiares y graduaciones"

RELIGIOUS_SCHOOL_EN = "your school masses, family events, fundraisers and graduations"
RELIGIOUS_SCHOOL_ES = "las misas escolares, eventos familiares, recaudaciones y graduaciones"

EDU_INST_EN = "your community events, registration drives and outdoor ceremonies"
EDU_INST_ES = "los eventos comunitarios, jornadas de inscripción y ceremonias al aire libre"

# Higher ed
UNIV_EN = "your orientation, alumni receptions, college fairs and commencement"
UNIV_ES = "la orientación, recepciones de exalumnos, ferias universitarias y graduación"

COLLEGE_EN = "your open houses, registration events and graduation receptions"
COLLEGE_ES = "los open houses, eventos de inscripción y recepciones de graduación"

# Vocational / specialty schools — open house + recruitment angle
VOCATIONAL_EN = "your open houses, recruitment events and graduation ceremonies"
VOCATIONAL_ES = "los open houses, eventos de reclutamiento y ceremonias de graduación"

# Sports / martial arts schools — outdoor tournaments + demos
SPORTS_SCHOOL_EN = "your tournaments, belt ceremonies and student showcase events"
SPORTS_SCHOOL_ES = "los torneos, ceremonias de cinta y demostraciones de alumnos"

DANCE_MUSIC_EN = "your recitals, student showcases and outdoor performances"
DANCE_MUSIC_ES = "los recitales, presentaciones de alumnos y muestras al aire libre"

GENERIC_EN = "your outdoor events and community gatherings"
GENERIC_ES = "los eventos al aire libre y reuniones comunitarias"


CATEGORY_MAP = {
    # --- Churches (generic + denominational) ---
    "Church":                       (CHURCH_GENERIC_EN, CHURCH_GENERIC_ES, "church"),
    "Christian church":             (NONDENOM_EN, NONDENOM_ES, "church"),
    "Non-denominational church":    (NONDENOM_EN, NONDENOM_ES, "church"),
    "Gospel church":                (NONDENOM_EN, NONDENOM_ES, "church"),
    "Religious organization":       (CHURCH_GENERIC_EN, CHURCH_GENERIC_ES, "church"),
    "Religious institution":        (CHURCH_GENERIC_EN, CHURCH_GENERIC_ES, "church"),
    "Religious destination":        (CHURCH_GENERIC_EN, CHURCH_GENERIC_ES, "church"),
    "Religious goods store":        (GENERIC_EN, GENERIC_ES, "other"),
    "Parish":                       (CATHOLIC_EN, CATHOLIC_ES, "church"),
    "Catholic church":              (CATHOLIC_EN, CATHOLIC_ES, "church"),
    "Baptist church":               (BAPTIST_EN, BAPTIST_ES, "church"),
    "Pentecostal church":           (HISPANIC_CHURCH_EN, HISPANIC_CHURCH_ES, "church"),
    "Apostolic church":             (HISPANIC_CHURCH_EN, HISPANIC_CHURCH_ES, "church"),
    "Hispanic church":              (HISPANIC_CHURCH_EN, HISPANIC_CHURCH_ES, "church"),
    "Methodist church":             (NONDENOM_EN, NONDENOM_ES, "church"),
    "United Methodist church":      (NONDENOM_EN, NONDENOM_ES, "church"),
    "Lutheran church":              (NONDENOM_EN, NONDENOM_ES, "church"),
    "Presbyterian church":          (NONDENOM_EN, NONDENOM_ES, "church"),
    "Episcopal church":             (NONDENOM_EN, NONDENOM_ES, "church"),
    "Anglican church":              (NONDENOM_EN, NONDENOM_ES, "church"),
    "Evangelical church":           (NONDENOM_EN, NONDENOM_ES, "church"),
    "Assemblies of God church":     (NONDENOM_EN, NONDENOM_ES, "church"),
    "Seventh-day Adventist church": (NONDENOM_EN, NONDENOM_ES, "church"),
    "Church of Christ":             (NONDENOM_EN, NONDENOM_ES, "church"),
    "Church of the Nazarene":       (NONDENOM_EN, NONDENOM_ES, "church"),
    "Calvary Chapel church":        (NONDENOM_EN, NONDENOM_ES, "church"),
    "Foursquare church":            (NONDENOM_EN, NONDENOM_ES, "church"),
    "Korean church":                (NONDENOM_EN, NONDENOM_ES, "church"),
    "Unity church":                 (NONDENOM_EN, NONDENOM_ES, "church"),
    "Unitarian Universalist Church":(NONDENOM_EN, NONDENOM_ES, "church"),
    "United Church of Christ":      (NONDENOM_EN, NONDENOM_ES, "church"),
    "Disciples of Christ Church":   (NONDENOM_EN, NONDENOM_ES, "church"),
    "Greek Orthodox church":        (NONDENOM_EN, NONDENOM_ES, "church"),
    "Eastern Orthodox Church":      (NONDENOM_EN, NONDENOM_ES, "church"),
    "Protestant church":            (NONDENOM_EN, NONDENOM_ES, "church"),
    "Church of Jesus Christ of Latter-day Saints": (NONDENOM_EN, NONDENOM_ES, "church"),
    # Jewish / synagogues
    "Synagogue":                    (JEWISH_EN, JEWISH_ES, "church"),
    "Orthodox synagogue":           (JEWISH_EN, JEWISH_ES, "church"),
    "Conservative synagogue":       (JEWISH_EN, JEWISH_ES, "church"),
    "Messianic synagogue":          (JEWISH_EN, JEWISH_ES, "church"),
    # Other faiths
    "Hindu temple":                 (EASTERN_TEMPLE_EN, EASTERN_TEMPLE_ES, "church"),
    "Buddhist temple":              (EASTERN_TEMPLE_EN, EASTERN_TEMPLE_ES, "church"),
    "Parsi temple":                 (EASTERN_TEMPLE_EN, EASTERN_TEMPLE_ES, "church"),
    "Shrine":                       (EASTERN_TEMPLE_EN, EASTERN_TEMPLE_ES, "church"),
    "Mosque":                       (MOSQUE_EN, MOSQUE_ES, "church"),

    # --- K-12 schools ---
    "Elementary school":            (ELEM_EN, ELEM_ES, "school_k12"),
    "Primary school":               (ELEM_EN, ELEM_ES, "school_k12"),
    "Kindergarten":                 (ELEM_EN, ELEM_ES, "school_k12"),
    "Middle school":                (MIDDLE_EN, MIDDLE_ES, "school_k12"),
    "High school":                  (HIGH_EN, HIGH_ES, "school_k12"),
    "Girls' high school":           (HIGH_EN, HIGH_ES, "school_k12"),
    "Preparatory school":           (HIGH_EN, HIGH_ES, "school_k12"),
    "K-12 school":                  (ELEM_EN, ELEM_ES, "school_k12"),
    "School":                       (ELEM_EN, ELEM_ES, "school_k12"),
    "School house":                 (ELEM_EN, ELEM_ES, "school_k12"),
    "Co-ed school":                 (HIGH_EN, HIGH_ES, "school_k12"),
    "International school":         (PRIVATE_K12_EN, PRIVATE_K12_ES, "school_k12"),
    "Bilingual school":             (ELEM_EN, ELEM_ES, "school_k12"),
    "Preschool":                    (PRESCHOOL_EN, PRESCHOOL_ES, "school_k12"),
    "Montessori school":            (MONTESSORI_EN, MONTESSORI_ES, "school_k12"),
    "Montessori preschool":         (PRESCHOOL_EN, PRESCHOOL_ES, "school_k12"),
    "Charter school":               (CHARTER_EN, CHARTER_ES, "school_k12"),
    "Private educational institution": (PRIVATE_K12_EN, PRIVATE_K12_ES, "school_k12"),
    "Religious school":             (RELIGIOUS_SCHOOL_EN, RELIGIOUS_SCHOOL_ES, "school_k12"),
    "Catholic school":              (RELIGIOUS_SCHOOL_EN, RELIGIOUS_SCHOOL_ES, "school_k12"),
    "Special education school":     (ELEM_EN, ELEM_ES, "school_k12"),
    "General education school":     (ELEM_EN, ELEM_ES, "school_k12"),
    "Public educational institution": (EDU_INST_EN, EDU_INST_ES, "school_k12"),
    "Educational institution":      (EDU_INST_EN, EDU_INST_ES, "school_k12"),
    "Military school":              (HIGH_EN, HIGH_ES, "school_k12"),
    "Gymnasium school":             (HIGH_EN, HIGH_ES, "school_k12"),

    # --- Higher ed ---
    "University":                   (UNIV_EN, UNIV_ES, "higher_ed"),
    "Public university":            (UNIV_EN, UNIV_ES, "higher_ed"),
    "Christian college":            (UNIV_EN, UNIV_ES, "higher_ed"),
    "College":                      (COLLEGE_EN, COLLEGE_ES, "higher_ed"),
    "Community college":            (COLLEGE_EN, COLLEGE_ES, "higher_ed"),
    "Graduate school":              (COLLEGE_EN, COLLEGE_ES, "higher_ed"),
    "Institute of technology":      (COLLEGE_EN, COLLEGE_ES, "higher_ed"),
    "Research institute":           (EDU_INST_EN, EDU_INST_ES, "higher_ed"),
    "Conservatory":                 (DANCE_MUSIC_EN, DANCE_MUSIC_ES, "higher_ed"),

    # --- Vocational / specialty ---
    "Trade school":                 (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Vocational school":            (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Technical school":             (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Beauty school":                (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Barber school":                (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Cosmetology":                  (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Nursing school":               (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Medical school":               (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Dental school":                (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Massage school":               (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Culinary school":              (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Cooking school":               (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Bartending school":            (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Computer training school":     (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Language school":              (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "English language school":      (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Aviation training institute":  (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Art school":                   (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Architecture school":          (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Engineering school":           (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Handicraft school":            (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Wrestling school":             (SPORTS_SCHOOL_EN, SPORTS_SCHOOL_ES, "vocational"),

    # --- Sports / martial arts / dance / music ---
    "Martial arts school":          (SPORTS_SCHOOL_EN, SPORTS_SCHOOL_ES, "sports"),
    "Karate school":                (SPORTS_SCHOOL_EN, SPORTS_SCHOOL_ES, "sports"),
    "Taekwondo school":             (SPORTS_SCHOOL_EN, SPORTS_SCHOOL_ES, "sports"),
    "Jujitsu school":               (SPORTS_SCHOOL_EN, SPORTS_SCHOOL_ES, "sports"),
    "Self defense school":          (SPORTS_SCHOOL_EN, SPORTS_SCHOOL_ES, "sports"),
    "Tai chi school":               (SPORTS_SCHOOL_EN, SPORTS_SCHOOL_ES, "sports"),
    "Sports school":                (SPORTS_SCHOOL_EN, SPORTS_SCHOOL_ES, "sports"),
    "Horse riding school":          (SPORTS_SCHOOL_EN, SPORTS_SCHOOL_ES, "sports"),
    "Dance school":                 (DANCE_MUSIC_EN, DANCE_MUSIC_ES, "sports"),
    "Ballet school":                (DANCE_MUSIC_EN, DANCE_MUSIC_ES, "sports"),
    "Music school":                 (DANCE_MUSIC_EN, DANCE_MUSIC_ES, "sports"),

    # --- After-school / community ---
    "After school program":         (ELEM_EN, ELEM_ES, "school_k12"),
    "Adult education school":       (EDU_INST_EN, EDU_INST_ES, "other"),
    "Emergency training school":    (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Fire fighters academy":        (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Police academy":               (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Firearms academy":             (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Driving school":               (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Truck driving school":         (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
    "Flight school":                (VOCATIONAL_EN, VOCATIONAL_ES, "vocational"),
}


# Categories where outreach is unlikely to land (admin offices, libraries,
# building names from the UTEP campus, etc). We keep them in a separate file so
# the user can decide if they want to add any back in.
EXCLUDE_CATEGORIES = {
    "School bus service",
    "School administration office",
    "University library",
    "University hospital",
    "School district office",
    "School center",   # mostly office buildings
    "Association / Organization",
}


def normalize(s):
    return (s or "").strip()


def main():
    if not SOURCE.exists():
        print(f"Source missing: {SOURCE}", file=sys.stderr)
        sys.exit(1)

    merged_rows = []
    excluded_rows = []
    seen_categories = {}

    with SOURCE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = normalize(row.get("title"))
            category = normalize(row.get("categories/0"))
            if not title:
                continue

            seen_categories[category] = seen_categories.get(category, 0) + 1

            # Reason-to-exclude checks ------------------------------------
            reason = None
            if not category:
                reason = "no_category"
            elif category in EXCLUDE_CATEGORIES:
                reason = "excluded_category"
            elif category not in CATEGORY_MAP:
                reason = "unmapped_category"

            base = {
                "title": title,
                "street": normalize(row.get("street")),
                "city": normalize(row.get("city")) or "El Paso",
                "state": normalize(row.get("state")) or "Texas",
                "phone": normalize(row.get("phone")),
                "website": normalize(row.get("website")),
                "category": category,
            }

            if reason:
                base["exclude_reason"] = reason
                excluded_rows.append(base)
                continue

            en, es, segment = CATEGORY_MAP[category]
            base["use_case_en"] = en
            base["use_case_es"] = es
            base["segment"] = segment
            merged_rows.append(base)

    # --- Write mail merge ready CSV ----------------------------------------
    merge_fields = [
        "title", "street", "city", "state", "phone", "website",
        "category", "segment", "use_case_en", "use_case_es",
    ]
    with OUT_MERGE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=merge_fields)
        w.writeheader()
        for r in merged_rows:
            w.writerow({k: r.get(k, "") for k in merge_fields})

    # --- Write excluded list -----------------------------------------------
    excluded_fields = ["title", "street", "city", "category", "exclude_reason", "phone", "website"]
    with OUT_EXCLUDED.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=excluded_fields)
        w.writeheader()
        for r in excluded_rows:
            w.writerow({k: r.get(k, "") for k in excluded_fields})

    # --- Write category reference -----------------------------------------
    with OUT_CATMAP.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["category", "count_in_source", "status", "segment", "use_case_en", "use_case_es"])
        for cat, n in sorted(seen_categories.items(), key=lambda kv: -kv[1]):
            if cat in CATEGORY_MAP:
                en, es, seg = CATEGORY_MAP[cat]
                status = "included"
            elif cat in EXCLUDE_CATEGORIES:
                en = es = ""
                seg = ""
                status = "excluded_by_rule"
            elif not cat:
                en = es = seg = ""
                status = "no_category"
            else:
                en = es = seg = ""
                status = "unmapped"
            w.writerow([cat, n, status, seg, en, es])

    # --- Summary -----------------------------------------------------------
    print(f"Source rows scanned: {sum(seen_categories.values())}")
    print(f"  -> mail merge ready: {len(merged_rows)}")
    print(f"  -> excluded:         {len(excluded_rows)}")
    print(f"Unique categories:   {len(seen_categories)}")
    print()
    print("Segment breakdown (merge-ready):")
    seg_counts = {}
    for r in merged_rows:
        seg_counts[r["segment"]] = seg_counts.get(r["segment"], 0) + 1
    for seg, n in sorted(seg_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {seg:<12} {n}")


if __name__ == "__main__":
    main()
