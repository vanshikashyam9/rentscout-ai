from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True)

    title = Column(String)
    price = Column(String)              # original scraped text, kept for display
    price_amount = Column(Integer)      # parsed integer dollars, used for logic
    location = Column(String)
    link = Column(String, unique=True)  # prevents duplicate listings

    bedrooms = Column(Integer)          # nullable until scraper extracts it
    property_type = Column(String)      # nullable until scraper extracts it
    scraped_at = Column(DateTime, default=datetime.utcnow)

    # Where the row came from: "craigslist" for scraped rows, "demo" for the
    # seeded sample data the public site runs on. The UI must not present a
    # demo row as a real listing with a working outbound link.
    source = Column(String, default="craigslist")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
