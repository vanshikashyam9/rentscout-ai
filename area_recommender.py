import pandas as pd

# Load cleaned dataset
df = pd.read_csv(
    "data/processed/cleaned_market_data.csv"
)

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