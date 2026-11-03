import logging
import threading

import pandas as pd
from sqlalchemy import text

from backend.database.database import engine
from backend.services import cmhc_loader

logger = logging.getLogger("rentscout.market")

# -----------------------------------
# DATA ACCESS
#
# The CMHC figures live in Postgres (zones, vacancy_rates, average_rents) and
# are loaded from data/processed/*.csv by services/cmhc_loader.py. Queries
# come back as DataFrames with the same columns the CSVs had, so the analysis
# below is unchanged.
#
# The tables are filled in the background right after startup, so a request
# can arrive before they exist. In that window, and if the database is down,
# we serve from the CSVs rather than erroring — and don't cache that result,
# so the next request picks up the database as soon as it is ready.
# -----------------------------------

_VACANCY_SQL = text("""
    SELECT z.name AS "Zone", v.vacancy_rate AS "Vacancy_Rate", v.year AS "Year"
    FROM vacancy_rates v JOIN zones z ON z.id = v.zone_id
    ORDER BY z.id, v.year
""")

_RENTS_SQL = text("""
    SELECT z.name AS "Zone", a.bedrooms AS "Bedrooms",
           a.average_rent AS "Average_Rent", a.survey AS "Survey"
    FROM average_rents a JOIN zones z ON z.id = a.zone_id
    ORDER BY z.id, a.bedrooms
""")

_cache = {}
_lock = threading.Lock()


def _load(key, sql, csv_reader):
    with _lock:
        if key in _cache:
            return _cache[key]
    try:
        frame = pd.read_sql(sql, engine)
        if not frame.empty:
            with _lock:
                _cache[key] = frame
            return frame
        logger.warning("%s table is empty; serving from CSV for now.", key)
    except Exception as exc:
        logger.warning("Could not read %s from database (%s); using CSV.",
                       key, exc.__class__.__name__)
    return csv_reader()


def get_vacancy_df():
    """CMHC vacancy rates: columns Zone, Vacancy_Rate, Year."""
    return _load("vacancy", _VACANCY_SQL, cmhc_loader.read_vacancy_csv)


def get_rents_df():
    """CMHC average rents: columns Zone, Bedrooms, Average_Rent, Survey."""
    return _load("rents", _RENTS_SQL, cmhc_loader.read_rents_csv)


def clear_cache():
    """Drop cached frames, e.g. after reloading the tables."""
    with _lock:
        _cache.clear()


def get_average_rent(area_name, bedrooms=None):
    """
    Average market rent for an area, from CMHC.

    bedrooms: 0-3 when known. Falls back to the cheapest bedroom type in the
    area, since any unit should cost at least roughly what a studio does —
    that keeps the comparison conservative rather than flagging a small unit
    for being cheaper than a three-bedroom average.

    Returns None when the area matches no CMHC zone.
    """
    rents_df = get_rents_df()
    matches = rents_df[
        rents_df["Zone"].str.contains(area_name, case=False, na=False)
    ]

    if matches.empty:
        return None

    if bedrooms is not None:
        # CMHC's largest category is "3 Bedroom +".
        capped = min(int(bedrooms), 3)
        exact = matches[matches["Bedrooms"] == capped]
        if not exact.empty:
            return {
                "average_rent": int(round(exact["Average_Rent"].mean())),
                "bedrooms": capped,
                "zones_matched": sorted(exact["Zone"].unique().tolist()),
                "survey": exact["Survey"].iloc[0],
            }

    cheapest = matches.loc[matches["Average_Rent"].idxmin()]

    return {
        "average_rent": int(cheapest["Average_Rent"]),
        "bedrooms": int(cheapest["Bedrooms"]),
        "zones_matched": [str(cheapest["Zone"])],
        "survey": str(cheapest["Survey"]),
    }

# -----------------------------------
# GET MARKET DATA FUNCTION
# -----------------------------------

def get_market_stats(area_name):

    df = get_vacancy_df()

    # Search matching zones
    matches = df[
        df["Zone"].str.contains(
            area_name,
            case=False,
            na=False
        )
    ]

    # No results
    if matches.empty:
        return None

    # Average vacancy rate
    avg_vacancy = matches["Vacancy_Rate"].mean()

    # Latest year data
    latest_year = matches["Year"].max()

    latest_data = matches[
        matches["Year"] == latest_year
    ]

    latest_vacancy = latest_data["Vacancy_Rate"].mean()

    return {
        "area": area_name,
        "average_vacancy": float(round(avg_vacancy, 2)),
        "latest_year": int(latest_year),
        "latest_vacancy": float(round(latest_vacancy, 2))
    }

def list_zones():
    """Every CMHC zone name, for the area picker on the market page."""
    return sorted(get_vacancy_df()["Zone"].unique().tolist())


def get_vacancy_trend(area_name):
    """
    Year-by-year vacancy rate for an area.

    An area string can match several CMHC zones (e.g. "Vancouver" matches the
    city rollup and every numbered zone), so rates are averaged per year and
    the matched zones are returned alongside for transparency.
    """
    df = get_vacancy_df()
    matches = df[
        df["Zone"].str.contains(area_name, case=False, na=False)
    ]

    if matches.empty:
        return None

    yearly = (
        matches.groupby("Year")["Vacancy_Rate"]
        .mean()
        .reset_index()
        .sort_values("Year")
    )

    return {
        "area": area_name,
        "zones_matched": sorted(matches["Zone"].unique().tolist()),
        "series": [
            {
                "year": int(row.Year),
                "vacancy_rate": float(round(row.Vacancy_Rate, 2)),
            }
            for row in yearly.itertuples()
        ],
    }


# -----------------------------------
# TEST ENGINE
# -----------------------------------

if __name__ == "__main__":

    result = get_market_stats("Downtown")

    print("\n📊 MARKET INTELLIGENCE RESULT:\n")

    print(result)