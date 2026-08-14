import os

import pandas as pd

# Anchored to the project root, not the shell's working directory, so the
# script runs the same from anywhere.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED = os.path.join(PROJECT_ROOT, "data", "processed")

# Load merged dataset
df = pd.read_csv(
    os.path.join(PROCESSED, "all_vancouver_vacancy_rates.csv")
)

print("📊 Original Dataset:\n")
print(df.head())

# -----------------------------------
# CLEAN VACANCY RATE
# -----------------------------------

# Replace invalid values
df["Vacancy_Rate"] = df["Vacancy_Rate"].replace("**", None)

# Convert to numeric
df["Vacancy_Rate"] = pd.to_numeric(
    df["Vacancy_Rate"],
    errors="coerce"
)

# Remove rows with missing values
df = df.dropna(subset=["Vacancy_Rate"])

# -----------------------------------
# CLEAN ZONE NAMES
# -----------------------------------

df["Zone"] = df["Zone"].str.strip()

# -----------------------------------
# RESET INDEX
# -----------------------------------

df = df.reset_index(drop=True)

# -----------------------------------
# SAVE CLEANED DATASET
# -----------------------------------

output_path = os.path.join(PROCESSED, "cleaned_market_data.csv")

df.to_csv(output_path, index=False)

print("\n✅ CLEANED DATASET SAVED")
print(f"📁 File: {output_path}")

print("\n📊 Cleaned Preview:\n")
print(df.head(20))

print("\n📈 Dataset Info:\n")
print(df.info())