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