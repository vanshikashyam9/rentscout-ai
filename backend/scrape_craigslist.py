"""
Local-only Craigslist scraper.

Deliberately NOT exposed as an API endpoint. A public scrape endpoint lets
anyone make the deployed server fetch from Craigslist using its own IP, which
risks a block and breaches their terms of service. The public site runs on the
seeded sample data instead — see backend/seed_data.py.

Run from the project root, on your own machine:
    venv/bin/python -m backend.scrape_craigslist
"""

from backend.database.database import SessionLocal
from backend.database.models import Rental
from backend.services.craigslist_scraper import get_craigslist_listings
from backend.services.price_utils import parse_price

SOURCE = "craigslist"


def run():
    listings = get_craigslist_listings()
    print(f"Fetched {len(listings)} listings.")

    db = SessionLocal()
    saved = 0

    try:
        for item in listings:
            exists = (
                db.query(Rental).filter(Rental.link == item["link"]).first()
            )
            if exists:
                continue

            db.add(
                Rental(
                    title=item["title"],
                    price=item["price"],
                    price_amount=parse_price(item["price"]),
                    location=item["location"],
                    link=item["link"],
                    source=SOURCE,
                )
            )
            saved += 1

        db.commit()
        print(f"Saved {saved} new listings ({len(listings) - saved} already known).")
    finally:
        db.close()


if __name__ == "__main__":
    run()
