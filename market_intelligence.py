import pandas as pd

# -----------------------------------
# LOAD DATASET
# -----------------------------------

df = pd.read_csv(
    "data/processed/cleaned_market_data.csv"
)

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

# -----------------------------------
# TEST ENGINE
# -----------------------------------

if __name__ == "__main__":

    result = get_market_stats("Downtown")

    print("\n📊 MARKET INTELLIGENCE RESULT:\n")

    print(result)