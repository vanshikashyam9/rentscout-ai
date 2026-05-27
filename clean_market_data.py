import pandas as pd

# Load merged dataset
df = pd.read_csv(
    "data/processed/all_vancouver_vacancy_rates.csv"
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

output_path = "data/processed/cleaned_market_data.csv"

df.to_csv(output_path, index=False)

print("\n✅ CLEANED DATASET SAVED")
print(f"📁 File: {output_path}")

print("\n📊 Cleaned Preview:\n")
print(df.head(20))

print("\n📈 Dataset Info:\n")
print(df.info())