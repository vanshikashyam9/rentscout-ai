import pandas as pd
import os

# -----------------------------------
# CONFIG
# -----------------------------------

RAW_FOLDER = "data/raw"
OUTPUT_FILE = "data/processed/all_vancouver_vacancy_rates.csv"

# Store all yearly dataframes
all_data = []

# -----------------------------------
# LOOP THROUGH FILES
# -----------------------------------

for filename in os.listdir(RAW_FOLDER):

    # Skip non-excel files
    if not filename.endswith(".xlsx"):
        continue

    # Extract year from filename
    year = filename.split("-")[2]

    # Build full file path
    file_path = os.path.join(RAW_FOLDER, filename)

    print(f"\n🚀 Processing {year}...")

    try:

        # Load CMHC table
        df = pd.read_excel(
            file_path,
            sheet_name="Table 1.1.1",
            header=None
        )

        # Extract useful columns
        clean_df = df.iloc[7:, [0, 23]]

        # Rename columns
        clean_df.columns = [
            "Zone",
            "Vacancy_Rate"
        ]

        # Remove empty rows
        clean_df = clean_df.dropna()

        # Reset index
        clean_df = clean_df.reset_index(drop=True)

        # Add year column
        clean_df["Year"] = int(year)

        # Append to master list
        all_data.append(clean_df)

        print(f"✅ {year} processed successfully")

    except Exception as e:
        print(f"❌ Error processing {year}:")
        print(e)

# -----------------------------------
# MERGE ALL YEARS
# -----------------------------------

if len(all_data) > 0:

    final_df = pd.concat(all_data, ignore_index=True)

    # Save final dataset
    final_df.to_csv(OUTPUT_FILE, index=False)

    print("\n🎉 ALL YEARS MERGED SUCCESSFULLY")
    print(f"📁 Saved to: {OUTPUT_FILE}")

    # Show preview
    print("\n📊 Preview:\n")
    print(final_df.head(20))

else:
    print("❌ No data processed")