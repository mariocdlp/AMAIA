# EP Fiesta — Summer 2026 Direct-Mail Campaign

Direct-mail outreach to El Paso churches, schools and community institutions. Each segment has its own letter — written to that audience's fall and December event calendar — pitching tents and shade with a "book 3 months in advance and get 15% off" offer.

## What's in this folder

| File | Purpose |
|---|---|
| `source/contacts_raw.csv` | Original scrape (1,197 rows). Don't edit. |
| `build_mailmerge.py` | Cleans, filters and segments the source. Re-run anytime. |
| `mailmerge_contacts.csv` | **The deliverable.** 1,103 deliverable contacts with `group_key` column to match against the right letter. |
| `excluded_contacts.csv` | 94 rows filtered out (no physical address, admin offices, libraries, etc.). |
| `category_map.csv` | Every category in the source mapped to its group. |
| `group_counts.csv` | Per-group deliverable counts (all >=25). |
| `letters/` | **15 distinct bilingual EN+ES letters**, one per group. |

## Filters applied

1. Drop any row without a physical street address (direct mail requires one).
2. Drop admin/transport/library/building rows (school district offices, university libraries, building names, etc.).
3. Map every remaining category to one of 15 groups.
4. Verify every group has at least 25 deliverable contacts; merge smaller groups into their nearest sibling.

## The 15 groups

| Group | Count | Letter | Audience |
|---|---:|---|---|
| `catholic` | 47 | `letters/catholic.md` | Catholic churches, Catholic schools, parishes |
| `baptist` | 40 | `letters/baptist.md` | Baptist churches |
| `pentecostal` | 25 | `letters/pentecostal.md` | Pentecostal, Apostolic, Assemblies of God, Foursquare, Hispanic |
| `mainline_protestant` | 61 | `letters/mainline_protestant.md` | Methodist, Lutheran, Presbyterian, Episcopal, Anglican, Nazarene, Church of Christ, Disciples, UCC, Orthodox, LDS |
| `evangelical` | 73 | `letters/evangelical.md` | Christian church, non-denominational, evangelical, Calvary Chapel, SDA, Gospel, Korean, Unity, UU |
| `generic_church` | 271 | `letters/generic_church.md` | Church (unspecified) + synagogues + Hindu/Buddhist/Mosque/Shrine |
| `elementary` | 172 | `letters/elementary.md` | Elementary, K-8 generalists, after-school programs |
| `middle_school` | 30 | `letters/middle_school.md` | Middle schools |
| `high_school` | 59 | `letters/high_school.md` | High schools (incl. prep, military, international) |
| `preschool` | 42 | `letters/preschool.md` | Preschool and Montessori |
| `private_k12` | 27 | `letters/private_k12.md` | Private, charter and religious K-12 |
| `higher_ed` | 81 | `letters/higher_ed.md` | Universities, colleges, community colleges, research institutes |
| `vocational` | 111 | `letters/vocational.md` | Trade, beauty, driving, medical, emergency, language and other specialty schools |
| `martial_arts` | 38 | `letters/martial_arts.md` | Martial arts, combat sports, riding schools |
| `dance_music` | 26 | `letters/dance_music.md` | Dance, ballet and music schools |
| **Total** | **1,103** | | |

## Theme

Every letter is built around the same offer: **book 3 months in advance and get 15% off the tent rental.** Because the campaign sends out in summer, every letter points the reader at the fall and December events specific to their world:

- Churches: Fall Festival, Trunk-or-Treat, Homecoming Sunday, kermés, Thanksgiving outreach, Christmas Eve services, Las Posadas, Día de la Virgen de Guadalupe.
- K-12 schools: Fall Festival, Veterans Day program, Thanksgiving family lunch, Winter Wonderland, Polar Express day, Winter Formal, December commencement.
- Higher Ed: Homecoming, alumni tailgate, October open house, donor receptions, December commencement.
- Vocational: Open house, recruitment fair, December cohort graduation.
- Martial arts: October belt promotion, in-house tournament, school anniversary, December student showcase.
- Dance & Music: Fall recital, Nutcracker, Christmas concert / Posada, end-of-year family event.

## Mail-merge fields used in every letter

- `{{title}}` — institution name (e.g., "Abundant Church")
- `{{street}}` — street address (e.g., "7100 N Desert Blvd")
- `{{city}}` — city (defaults to "El Paso")

## How to run a mail merge from this

1. Open `mailmerge_contacts.csv` in Google Sheets or your CRM.
2. **Split the sheet by `group_key`** — one filter view per group.
3. For each group, open `letters/<group_key>.md`, copy the body into your mail-merge tool (YAMM, Mailchimp, Word merge, etc.), connect to the filtered sheet, and send.
4. The `{{field}}` braces work with Mustache/Handlebars-based tools; for Mailchimp swap them to `*|TITLE|*` syntax.

## Sender block (used in every letter)

> — Mario
> EP Fiesta · Party Rentals El Paso
> epfiesta.com · (915) 268-3997

Change the name/title in each letter if a different person is signing.
