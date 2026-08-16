import pandas as pd

# -----------------------------------
# LOAD DATASET
# -----------------------------------

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# services/ -> backend/ -> project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))

CSV_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "cleaned_market_data.csv"
)

df = pd.read_csv(CSV_PATH)

RENTS_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "cmhc_average_rents.csv"
)

# CMHC average rents by zone and bedroom type, from Table 1.1.2 of the Rental
# Market Survey. Real market figures — the scam detector's price check reads
# these rather than asking prices from listings in our own database.
rents_df = pd.read_csv(RENTS_PATH)


def get_average_rent(area_name, bedrooms=None):
    """
    Average market rent for an area, from CMHC.

    bedrooms: 0-3 when known. Falls back to the cheapest bedroom type in the
    area, since any unit should cost at least roughly what a studio does —
    that keeps the comparison conservative rather than flagging a small unit
    for being cheaper than a three-bedroom average.

    Returns None when the area matches no CMHC zone.
    """
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
    return sorted(df["Zone"].unique().tolist())


def get_vacancy_trend(area_name):
    """
    Year-by-year vacancy rate for an area.

    An area string can match several CMHC zones (e.g. "Vancouver" matches the
    city rollup and every numbered zone), so rates are averaged per year and
    the matched zones are returned alongside for transparency.
    """
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