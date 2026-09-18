"""Categorization rules. First match wins. Order matters.

Each rule: (regex, account_code, confidence, note)
confidence: "high" = merchant is unambiguous; "review" = Mario should confirm.
"""
import re

TRANSFER = "9010"

RULES = [
    # ---- interaccount transfers: never income or expense -------------------
    (r"APPLECARD GSBANK|ACH DEPOSIT INTERNET TRANSFER FROM ACCOUNT", TRANSFER, "high", "Chase -> Apple Card payment"),
    (r"CAPITAL ONE (MOBILE|ONLINE) PYMT|ORIG CO NAME:CAPITAL ONE", TRANSFER, "high", "Chase -> Capital One payment"),

    # ---- owner equity -------------------------------------------------------
    (r"ONLINE ACH PAYMENT.*JMCHOW", "3020", "high", "Transfer to owner personal account = draw"),
    (r"DEPOSIT\s+ID NUMBER", "3010", "review", "Large round deposit - confirm owner capital vs customer cash"),

    # ---- revenue / other income --------------------------------------------
    (r"EPFIESTA\.COM", "4010", "high", "Stripe payout of customer payments (net of fees)"),
    (r"FULLSTEAM", "4010", "high", "Fullsteam payout of customer payments (net of fees)"),
    (r"CREDIT-CASH BACK REWARD", "7020", "high", "Credit card cash back"),
    (r"BUSINESS BANKING TIERED", "7020", "high", "Bank account bonus"),

    # ---- sales tax remitted to Texas ---------------------------------------
    (r"WEBFILE TAX PYMT", "2300", "high", "Texas Comptroller sales tax remittance - liability, not expense"),

    # ---- rental fleet: capitalized -----------------------------------------
    (r"CELINA TENT", "1520", "high", "Tent manufacturer - rental fleet"),
    (r"SP TABLECLOTHSFACTOR", "1530", "high", "Tablecloths - linen fleet"),

    # ---- sub-rentals --------------------------------------------------------
    (r"IMPACT PARTY R", "5010", "high", "Impact Party Rentals - sub-rental to fill an order"),

    # ---- event labor (paid via Cash App / Zelle) ---------------------------
    (r"CASH APP\*(RICARDO LOZANO|KENNY RAW|RAUL RUIZ|RAMONA RODRIGU|DIEGO CONOR|JUAN SOTELO)", "5040", "high", "Event crew - track for 1099"),
    (r"ZELLE PAYMENT TO (GABY|GABRIELA) MARROQUIN", "5040", "high", "Event crew - track for 1099"),

    # ---- delivery & vehicle -------------------------------------------------
    (r"CIRCLE ?K|MURPHY EXPRESS|SPEEDWAY|SAMS ?CLUB #8153|SAM'S CLUB.*GAS", "5020", "high", "Fuel for delivery runs"),
    (r"MISTER CAR WASH", "5030", "high", "Delivery vehicle cleaning"),
    (r"TRAILERPLUS", "5030", "high", "Trailer supplies"),

    # ---- repairs / hardware -------------------------------------------------
    (r"NUTS & BOLTS|CANUTILLO ACE HARDWARE", "5070", "high", "Hardware for equipment repair"),
    (r"THE HOME DEPOT|LOWE'S|LOWES", "5070", "review", "Hardware - split fleet build vs repair"),

    # ---- insurance ----------------------------------------------------------
    (r"NEXT INSUR", "6030", "high", "Next Insurance business owner policy"),

    # ---- advertising & lead generation -------------------------------------
    (r"GOOGLE\s*\*?ADS|GOOGLE ADS", "6100", "high", "Google Ads"),
    (r"THE KNOT", "6110", "high", "Wedding lead generation"),
    (r"ONLINEPRINT|360ONLINEPRINT", "6100", "high", "Printed marketing material"),
    (r"LOCALFALCON", "6110", "high", "Local SEO rank tracking"),

    # ---- rental management software ----------------------------------------
    (r"PST\*?EVENT RENTAL SYSTE|EVENT RENTAL SYSTE", "6200", "high", "Event Rental Systems - rental management software"),
    (r"BOOQABLE", "6200", "high", "Booqable - rental management software"),

    # ---- general software & subscriptions ----------------------------------
    (r"OPENAI|SPEED-AI|DESCRIPT|MAKE\.COM|EXPRESSVPN|WHATSNAP|GOOGLE WORKSPACE|GOOGLE\*CLOUD|GOOGLE L8BDXZ|SQSP|BIG MEDIA|APPLEVEL|APPLE SERVICES", "6200", "high", "Software subscription"),
    (r"P\.SKOOL\.COM|9X12 METHOD|AUDIBLE", "6200", "review", "Education / media subscription - confirm business purpose"),

    # ---- office / admin -----------------------------------------------------
    (r"THE UPS STORE", "6300", "high", "Shipping and postage"),
    (r"TEXAS SECRETARY OF STA|TEXAS S\.O\.S\.", "6700", "high", "State filing fee"),

    # ---- meals --------------------------------------------------------------
    (r"WHATABURGER|GORDITAS|BARBACOA|LOS PRIMOS|LOST IN EL PASO|T5 EL PASO|LA MALINCHE|LOST IN", "6900", "high", "Meals - 50% deductible"),
    (r"CTLP\*EL PASO GYMNASTIC", "6900", "review", "Small charge - confirm"),

    # ---- likely personal ----------------------------------------------------
    (r"WHOLEFDS|WHOLE FOODS|TARGET|WAL-?MART #", "3020", "review", "Grocery/retail - likely personal, confirm"),
    (r"TEMU", "3020", "review", "Likely personal, confirm"),
]

# Specific transactions identified from email receipts, keyed by (date, abs(amount)).
# These override the merchant rules above.
EMAIL_IDENTIFIED = {
    ("2026-09-16", 649.40): ("1510", "high", "Amazon: 5x TRINEAR white folding tables/chairs - rental fleet"),
    ("2026-08-28", 205.66): ("1520", "high", "Amazon: CROWN SHADES commercial canopy - rental fleet"),
    ("2026-09-16", 43.29):  ("5080", "high", "Amazon: Simpli-Magic moving blankets - fleet protection"),
    ("2026-09-04", 259.74): ("5050", "review", "Sam's Club pickup order - confirm contents"),
    ("2026-09-06", 15.14):  ("6300", "review", "Amazon: Staples ergonomic office chair"),
    # Pool maintenance cluster - almost certainly the household pool, not the rental business
    ("2026-07-12", 132.05): ("3020", "review", "Amazon: Clorox Pool&Spa chemicals - appears personal"),
    ("2026-06-05", 81.13):  ("3020", "review", "Amazon: Hayward pool filter - appears personal"),
    ("2026-06-05", 16.76):  ("3020", "review", "Amazon: LubeTube O-ring grease (pool) - appears personal"),
    ("2026-08-24", 14.06):  ("3020", "review", "Amazon: nutrition item - appears personal"),
    ("2026-08-19", 216.47):  ("3020", "review", "eBay purchase - confirm business purpose"),
    # May fleet build-out: Eurmax 10x20 pop-up canopy + 22 more items
    ("2026-05-21", 259.65): ("1520", "high", "Amazon: Eurmax 10x20 pop-up canopy order - rental fleet"),
    ("2026-06-24", 73.00):  ("6100", "review", "Amazon: Hollyland wireless mic - content/marketing gear"),
    ("2026-06-22", 50.00):  ("6100", "review", "Amazon: UBeesize tripod - content/marketing gear"),
    ("2026-07-13", 97.38):  ("5080", "high", "Amazon: 3x 50ft outdoor extension cords - event power"),
    ("2026-07-13", 15.98):  ("5080", "high", "Amazon: Master Lock padlock - warehouse"),
    ("2026-07-14", 68.88):  ("1650", "review", "Amazon: wall mount storage racks - warehouse equipment"),
}

COMPILED = [(re.compile(p, re.I), a, c, n) for p, a, c, n in RULES]

# Amazon / warehouse-club default when no specific identification exists.
BULK_DEFAULT = (
    re.compile(r"AMAZON|AMZN|SAMS ?CLUB|SAM'S CLUB|WALMART\.COM|EBAY|SAMSCLUB", re.I),
    "5080", "review", "Mixed-use retailer - default to event supplies, confirm from receipt",
)


def classify(description, date, amount):
    key = (date, round(abs(amount), 2))
    if key in EMAIL_IDENTIFIED:
        return EMAIL_IDENTIFIED[key]
    for rx, acct, conf, note in COMPILED:
        if rx.search(description):
            return acct, conf, note
    rx, acct, conf, note = BULK_DEFAULT
    if rx.search(description):
        return acct, conf, note
    return "6990", "review", "Unmatched - needs classification"
