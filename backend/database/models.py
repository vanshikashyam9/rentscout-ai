from datetime import datetime

from sqlalchemy import (
    Column, Float, ForeignKey, Integer, String, DateTime, UniqueConstraint
)
from sqlalchemy.orm import relationship
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


# ---------------------------------------------------------------------------
# CMHC Rental Market Survey data
#
# Loaded from data/processed/*.csv by backend/services/cmhc_loader.py. Three
# tables rather than one flat one: a zone is a real entity that both vacancy
# rates and average rents point at, so the zone name is stored once.
# ---------------------------------------------------------------------------

class Zone(Base):
    """A CMHC survey zone, e.g. "Zone 19 - Richmond", or a rollup such as
    "Vancouver CMA" or "City of Vancouver (Zones 1-10)"."""
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    vacancy_rates = relationship(
        "VacancyRate", back_populates="zone", cascade="all, delete-orphan"
    )
    average_rents = relationship(
        "AverageRent", back_populates="zone", cascade="all, delete-orphan"
    )


class VacancyRate(Base):
    """Purpose-built rental vacancy rate (%) for one zone in one survey year.
    Some zone/years are suppressed by CMHC and simply have no row."""
    __tablename__ = "vacancy_rates"
    __table_args__ = (UniqueConstraint("zone_id", "year"),)

    id = Column(Integer, primary_key=True)
    zone_id = Column(
        Integer, ForeignKey("zones.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    year = Column(Integer, nullable=False)
    vacancy_rate = Column(Float, nullable=False)

    zone = relationship("Zone", back_populates="vacancy_rates")


class AverageRent(Base):
    """CMHC average monthly rent for a zone by bedroom count (0 = studio,
    3 = "3 bedroom +")."""
    __tablename__ = "average_rents"
    __table_args__ = (UniqueConstraint("zone_id", "bedrooms"),)

    id = Column(Integer, primary_key=True)
    zone_id = Column(
        Integer, ForeignKey("zones.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    bedrooms = Column(Integer, nullable=False)
    average_rent = Column(Integer, nullable=False)
    survey = Column(String)  # e.g. "Oct-25"

    zone = relationship("Zone", back_populates="average_rents")
