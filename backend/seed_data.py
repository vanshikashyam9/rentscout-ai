"""
Seed the rentals table with realistic Metro Vancouver sample listings.

The public deployment runs on this data rather than scraped listings, so the
site works for any visitor without republishing another platform's content.

Area labels are chosen to substring-match the CMHC zone names in
data/processed/cleaned_market_data.csv, so /market-stats?area=<location>
resolves for every seeded listing.

Run from the project root:
    venv/bin/python -m backend.seed_data            # replace demo rows
    venv/bin/python -m backend.seed_data --reset    # wipe all rentals first
"""

import argparse
import random
from datetime import datetime, timedelta

from sqlalchemy import text

from backend.database.database import engine, SessionLocal
from backend.database.models import Rental

SOURCE = "demo"

# Deterministic output: re-seeding produces the same listings every time.
SEED = 20260813

# (location label, typical 1-bedroom asking rent)
AREAS = [
    ("Downtown", 2650),
    ("West End", 2500),
    ("Kitsilano", 2450),
    ("Kerrisdale", 2400),
    ("North Vancouver", 2400),
    ("Mount Pleasant", 2350),
    ("Metrotown", 2300),
    ("Richmond", 2200),
    ("North Burnaby", 2150),
    ("Marpole", 2100),
    ("Tri-Cities", 2050),
    ("Southeast Vancouver", 2050),
    ("New Westminster", 2000),
    ("East Hastings", 1950),
    ("White Rock", 1950),
    ("Surrey", 1850),
    ("Delta", 1850),
    ("Langley", 1800),
    ("Maple Ridge", 1750),
]

# bedrooms -> (label, rent multiplier relative to a 1-bedroom)
UNIT_TYPES = [
    (0, "Studio", 0.78),
    (1, "1 Bed", 1.00),
    (2, "2 Bed", 1.36),
    (3, "3 Bed", 1.72),
]

# One- and two-bedroom units dominate the real market.
UNIT_WEIGHTS = [15, 35, 35, 15]

# Enough listings per area that a median asking rent is meaningful — the scam
# detector compares against it, and it needs more than two or three samples.
LISTINGS_PER_AREA = (5, 8)

# Not every unit size comes in every building type — a studio townhouse or a
# three-bedroom laneway house would read as obviously generated.
PROPERTY_TYPES_BY_BEDROOMS = {
    0: ["Apartment", "Condo", "Basement Suite"],
    1: ["Apartment", "Condo", "Basement Suite", "Laneway House"],
    2: ["Apartment", "Condo", "Townhouse", "Basement Suite"],
    3: ["Apartment", "Condo", "Townhouse"],
}

# Dense high-rise neighbourhoods: no basement suites or laneway houses.
APARTMENT_ONLY_AREAS = {"Downtown", "West End", "Metrotown"}

DESCRIPTORS = [
    "Bright",
    "Renovated",
    "Spacious",
    "Modern",
    "Quiet",
    "Sunny",
    "Newly Built",
    "Well-Kept",
]

FEATURES = [
    "in-suite laundry",
    "parking included",
    "steps to SkyTrain",
    "pet friendly",
    "balcony",
    "utilities included",
    "near shops and transit",
    "south-facing windows",
]


def build_listings():
    """Generate the sample listings deterministically."""
    rng = random.Random(SEED)
    now = datetime.utcnow()
    listings = []

    for area, base_rent in AREAS:
        count = rng.randint(*LISTINGS_PER_AREA)
        for bedrooms, unit_label, multiplier in rng.choices(
            UNIT_TYPES, weights=UNIT_WEIGHTS, k=count
        ):
            # ±6% jitter so prices don't look generated off a fixed formula.
            jitter = rng.uniform(-0.06, 0.06)
            amount = int(round(base_rent * multiplier * (1 + jitter) / 25) * 25)

            candidates = PROPERTY_TYPES_BY_BEDROOMS[bedrooms]
            if area in APARTMENT_ONLY_AREAS:
                candidates = [
                    t for t in candidates if t in ("Apartment", "Condo")
                ]
            property_type = rng.choice(candidates)
            title = (
                f"{rng.choice(DESCRIPTORS)} {unit_label} {property_type} "
                f"in {area} — {rng.choice(FEATURES)}"
            )

            listings.append(
                {
                    "title": title,
                    "price": f"${amount:,}",
                    "price_amount": amount,
                    "location": area,
                    "bedrooms": bedrooms,
                    "property_type": property_type,
                    # Deliberately not an http(s) URL. These listings do not
                    # exist, so nothing should be able to render a link that
                    # looks like it leads to a real posting.
                    "link": f"demo://listing/{len(listings) + 1}",
                    "scraped_at": now - timedelta(days=rng.randint(0, 21)),
                    "source": SOURCE,
                }
            )

    return listings


def run(reset: bool = False):
    # The column is new; older databases won't have it yet.
    with engine.begin() as conn:
        conn.execute(
            text("ALTER TABLE rentals ADD COLUMN IF NOT EXISTS source VARCHAR")
        )
        conn.execute(
            text("UPDATE rentals SET source = 'craigslist' WHERE source IS NULL")
        )

    db = SessionLocal()
    try:
        if reset:
            removed = db.query(Rental).delete()
            print(f"Deleted all {removed} rental rows.")
        else:
            removed = (
                db.query(Rental).filter(Rental.source == SOURCE).delete()
            )
            print(f"Deleted {removed} existing demo rows.")

        listings = build_listings()
        db.bulk_insert_mappings(Rental, listings)
        db.commit()

        prices = [item["price_amount"] for item in listings]
        print(
            f"Seeded {len(listings)} demo listings across {len(AREAS)} areas "
            f"(${min(prices):,}–${max(prices):,})."
        )
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reset",
        action="store_true",
        help="delete every rental row before seeding, not just demo rows",
    )
    run(reset=parser.parse_args().reset)
