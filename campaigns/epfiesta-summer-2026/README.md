# EP Fiesta — Summer 2026 Mail Merge Campaign

Outreach to El Paso churches, schools and community institutions, pitching tents and shade for outdoor events.

## What's in this folder

| File | Purpose |
|---|---|
| `source/contacts_raw.csv` | Original scrape (1,197 rows). Don't edit. |
| `build_mailmerge.py` | Cleans + segments the source, builds the merge-ready CSV. Re-run anytime. |
| `mailmerge_contacts.csv` | **The deliverable.** 1,165 contacts ready for mail merge with per-row personalization fields. |
| `excluded_contacts.csv` | 32 rows we filtered out (district offices, libraries, transportation, etc.). Add any back manually if you want them included. |
| `category_map.csv` | Reference: every category in the source, how many rows it covers, and the EN/ES pitch we wrote for it. |
| `letter_template_bilingual.md` | The bilingual letter template with `{{field}}` placeholders. |

## Numbers

- 1,165 ready-to-send contacts across 6 segments:
  - **church**: 546 (largest segment — denominational and non-denominational)
  - **school_k12**: 351 (elementary through high school + private + religious)
  - **vocational**: 109 (trade, beauty, nursing, driving schools, etc.)
  - **higher_ed**: 86 (UTEP campus buildings, EPCC, community colleges)
  - **sports**: 65 (martial arts, dance, music schools)
  - **other**: 8

## Per-category personalization

Each row carries a `use_case_en` and `use_case_es` field tailored to the institution type. Examples:

- Catholic church → "your parish kermés, first communions, confirmaciones and outdoor masses"
- Baptist church → "your Vacation Bible School, summer revivals, homecomings and outdoor baptisms"
- Elementary school → "your field day, fall carnival, back-to-school night and end-of-year celebration"
- High school → "your graduation, homecoming, prom afterparties and outdoor sports tournaments"
- Martial arts school → "your tournaments, belt ceremonies and student showcase events"

Full mapping in `category_map.csv`.

## How to run a mail merge from this

1. Open `mailmerge_contacts.csv` in Google Sheets (or your tool of choice).
2. Open `letter_template_bilingual.md` and copy the letter body into a Google Doc / email composer.
3. Hook the doc up to the sheet with **YAMM** (Google) or **Mailchimp** or your CRM of choice. The `{{field}}` braces work with Mustache/Handlebars-based merge tools; for Mailchimp swap to `*|TITLE|*` style.
4. Recommended send batches: split by `segment` column so you can A/B test subject lines independently per segment.

## Offer being made

15% off when the customer books at least 3 months in advance. This rewards the buyer planning their fall/back-to-school event today and pushes margin (vs blanket discount on last-minute bookings).
