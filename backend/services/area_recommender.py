import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# services/ -> backend/ -> project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))

csv_path = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "cleaned_market_data.csv"
)

df = pd.read_csv(csv_path)

def recommend_areas(budget):

    latest_year = df["Year"].max()

    latest_df = df[
        df["Year"] == latest_year
    ]

    recommendations = []

    for _, row in latest_df.iterrows():

        area = row["Zone"]
        vacancy = row["Vacancy_Rate"]

        score = 0

        # -----------------------------------
        # Vacancy logic
        # -----------------------------------

        if vacancy >= 4:
            score += 3

        elif vacancy >= 2:
            score += 2

        elif vacancy >= 1:
            score += 1

        # -----------------------------------
        # Budget logic
        # -----------------------------------

        if budget < 1800:

            if any(x in area.lower() for x in [
                "surrey",
                "langley",
                "maple ridge",
                "new westminster"
            ]):
                score += 3

        elif budget < 2500:

            if any(x in area.lower() for x in [
                "burnaby",
                "richmond",
                "tri-cities"
            ]):
                score += 3

        else:
            score += 2

        recommendations.append({
            "area": area,
            "vacancy_rate": vacancy,
            "score": score
        })

    recommendations = sorted(
        recommendations,
        key=lambda x: x["score"],
        reverse=True
    )

    return recommendations[:5]