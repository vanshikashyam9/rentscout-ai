"""
Load the processed CMHC CSVs into Postgres.

    python -m backend.services.cmhc_loader            # load if tables are empty
    python -m backend.services.cmhc_loader --reload   # wipe and reload

The API also calls load_if_empty() on startup, so a fresh database fills
itself the same way the demo listings do. The CSVs under data/processed/
remain the source of truth; the tables are what the API reads at runtime.
"""

import argparse
import logging
import os

import pandas as pd

from backend.database.database import SessionLocal, engine
from backend.database.models import AverageRent, Base, VacancyRate, Zone

logger = logging.getLogger("rentscout.cmhc")

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
PROCESSED = os.path.join(PROJECT_ROOT, "data", "processed")
VACANCY_CSV = os.path.join(PROCESSED, "cleaned_market_data.csv")
RENTS_CSV = os.path.join(PROCESSED, "cmhc_average_rents.csv")


def read_vacancy_csv():
    return pd.read_csv(VACANCY_CSV)


def read_rents_csv():
    return pd.read_csv(RENTS_CSV)


def load(reload=False):
    """Insert zones, vacancy rates and average rents. Returns row counts.

    Runs in one transaction, so a failure leaves the tables as they were.
    """
    vacancy = read_vacancy_csv()
    rents = read_rents_csv()

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if reload:
            # Children first; zones last.
            db.query(VacancyRate).delete()
            db.query(AverageRent).delete()
            db.query(Zone).delete()
            db.flush()

        # Zones in order of first appearance, so ids are stable run to run.
        names = list(dict.fromkeys(
            list(vacancy["Zone"]) + list(rents["Zone"])
        ))
        zone_ids = {}
        for name in names:
            zone = Zone(name=name)
            db.add(zone)
            db.flush()
            zone_ids[name] = zone.id

        db.add_all(
            VacancyRate(
                zone_id=zone_ids[r.Zone],
                year=int(r.Year),
                vacancy_rate=float(r.Vacancy_Rate),
            )
            for r in vacancy.itertuples()
        )
        db.add_all(
            AverageRent(
                zone_id=zone_ids[r.Zone],
                bedrooms=int(r.Bedrooms),
                average_rent=int(round(r.Average_Rent)),
                survey=str(r.Survey),
            )
            for r in rents.itertuples()
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    counts = {
        "zones": len(names),
        "vacancy_rates": len(vacancy),
        "average_rents": len(rents),
    }
    logger.info("Loaded CMHC data: %s", counts)
    return counts


def load_if_empty():
    """Load only when the zones table has no rows. Never overwrites."""
    db = SessionLocal()
    try:
        if db.query(Zone).count() > 0:
            return None
    finally:
        db.close()
    logger.info("No CMHC data found — loading from CSV.")
    return load()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--reload", action="store_true",
                        help="delete existing CMHC rows first")
    print(load(reload=parser.parse_args().reload))
