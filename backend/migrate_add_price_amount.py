"""
One-time migration: add new columns to the rentals table and backfill
price_amount from the existing price strings.

Safe to run more than once. Run from the project root:
    venv/bin/python -m backend.migrate_add_price_amount
"""

from sqlalchemy import text

from backend.database.database import engine, SessionLocal
from backend.database.models import Rental
from backend.services.price_utils import parse_price

NEW_COLUMNS = [
    "ALTER TABLE rentals ADD COLUMN IF NOT EXISTS price_amount INTEGER",
    "ALTER TABLE rentals ADD COLUMN IF NOT EXISTS bedrooms INTEGER",
    "ALTER TABLE rentals ADD COLUMN IF NOT EXISTS property_type VARCHAR",
    "ALTER TABLE rentals ADD COLUMN IF NOT EXISTS scraped_at TIMESTAMP",
]


def run():
    with engine.begin() as conn:
        for stmt in NEW_COLUMNS:
            conn.execute(text(stmt))
    print("Columns added (or already present).")

    db = SessionLocal()
    try:
        rentals = db.query(Rental).all()
        updated = 0
        skipped = 0
        for r in rentals:
            parsed = parse_price(r.price)
            if parsed is not None:
                r.price_amount = parsed
                updated += 1
            else:
                skipped += 1
        db.commit()
        print(f"Backfilled {updated} rows. Skipped {skipped} (unparseable price).")
    finally:
        db.close()


if __name__ == "__main__":
    run()
