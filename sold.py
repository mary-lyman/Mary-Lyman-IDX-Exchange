

import pandas as pd
import glob

# ============================================================
# Week 1: Load, Combine, and Filter Sold Data
# ============================================================

sold_files = glob.glob("CRMLSSold*.csv")

print("Files being combined:")
print(sold_files)

frames = []

for file in sold_files:
    df = pd.read_csv(file, encoding="ISO-8859-1", low_memory=False)
    print(f"{file} row count before append: {len(df)}")
    frames.append(df)

sold = pd.concat(frames, ignore_index=True)

print("\nRows after concatenation:", len(sold))

print("\nPropertyType frequency before filtering:")
print(sold["PropertyType"].value_counts(dropna=False))

sold = sold[sold["PropertyType"] == "Residential"]

print("\nRows after Residential filter:", len(sold))

print("\nPropertyType frequency after filtering:")
print(sold["PropertyType"].value_counts(dropna=False))


# ============================================================
# Week 2: Dataset Checks, Null Analysis, and Summary Statistics
# ============================================================

print("\nDataset shape:")
print(sold.shape)

print("\nColumn names:")
print(sold.columns)

print("\nData types:")
print(sold.dtypes)

print("\nFirst 5 rows:")
print(sold.head())

print("\nUnique PropertyType Values:")
print(sold["PropertyType"].unique())

print("\nNull count by column:")
null_counts = sold.isnull().sum()
print(null_counts)

print("\nMissing percentage by column:")
missing_percent = (sold.isnull().sum() / len(sold)) * 100
print(missing_percent)

print("\nColumns with more than 90% missing values:")
high_missing = missing_percent[missing_percent > 90]
print(high_missing)

print("\nSuggested columns to drop (>90% missing):")
print(high_missing.index.tolist())

null_summary = pd.DataFrame({
    "NullCount": null_counts,
    "MissingPercent": missing_percent
})

null_summary.to_csv("sold_null_summary.csv", index=True)

print("\nSaved sold_null_summary.csv")

numeric_columns = [
    "ClosePrice",
    "ListPrice",
    "LivingArea",
    "DaysOnMarket"
]

for column in numeric_columns:
    if column in sold.columns:
        print(f"\nSummary statistics for {column}:")
        print(sold[column].describe())

print("\nMedian ClosePrice:", sold["ClosePrice"].median())
print("Average ClosePrice:", sold["ClosePrice"].mean())

print("\nPercentage sold above list price:")
print((sold["ClosePrice"] > sold["ListPrice"]).mean() * 100)


# ============================================================
# Week 3: Mortgage Rate Data and Merge
# ============================================================

url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url)

print("\nMortgage columns:")
print(mortgage.columns)

mortgage.columns = ["date", "rate_30yr_fixed"]

mortgage["date"] = pd.to_datetime(mortgage["date"], errors="coerce")

mortgage["year_month"] = mortgage["date"].dt.to_period("M")

mortgage_monthly = mortgage.groupby(
    "year_month"
)["rate_30yr_fixed"].mean().reset_index()

sold["year_month"] = pd.to_datetime(
    sold["CloseDate"],
    errors="coerce"
).dt.to_period("M")

sold_with_rates = sold.merge(
    mortgage_monthly,
    on="year_month",
    how="left"
)

print("\nMissing mortgage rates in sold data:")
print(sold_with_rates["rate_30yr_fixed"].isnull().sum())

print("\nSold preview with mortgage rates:")
print(
    sold_with_rates[
        [
            "CloseDate",
            "year_month",
            "ClosePrice",
            "rate_30yr_fixed"
        ]
    ].head()
)


# ============================================================
# Week 4: Basic Data Cleaning
# ============================================================

sold_cleaned = sold_with_rates.copy()

print("\n--- Week 4 Cleaning ---")
print("Rows before cleaning:", len(sold_cleaned))
print("Columns before cleaning:", len(sold_cleaned.columns))

date_columns = [
    "CloseDate",
    "ListingContractDate",
    "PurchaseContractDate",
    "ContractStatusChangeDate"
]

for col in date_columns:
    if col in sold_cleaned.columns:
        sold_cleaned[col] = pd.to_datetime(
            sold_cleaned[col],
            errors="coerce"
        )

print("\nDate columns converted")

numeric_columns = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "DaysOnMarket",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "Latitude",
    "Longitude",
    "rate_30yr_fixed"
]

for col in numeric_columns:
    if col in sold_cleaned.columns:
        sold_cleaned[col] = pd.to_numeric(
            sold_cleaned[col],
            errors="coerce"
        )

print("Numeric columns converted")

rows_before_invalid = len(sold_cleaned)

if "ClosePrice" in sold_cleaned.columns:
    sold_cleaned = sold_cleaned[sold_cleaned["ClosePrice"] > 0]

if "ListPrice" in sold_cleaned.columns:
    sold_cleaned = sold_cleaned[sold_cleaned["ListPrice"] > 0]

if "LivingArea" in sold_cleaned.columns:
    sold_cleaned = sold_cleaned[sold_cleaned["LivingArea"] > 0]

if "DaysOnMarket" in sold_cleaned.columns:
    sold_cleaned = sold_cleaned[sold_cleaned["DaysOnMarket"] >= 0]

if "BedroomsTotal" in sold_cleaned.columns:
    sold_cleaned = sold_cleaned[sold_cleaned["BedroomsTotal"] >= 0]

if "BathroomsTotalInteger" in sold_cleaned.columns:
    sold_cleaned = sold_cleaned[sold_cleaned["BathroomsTotalInteger"] >= 0]

print("\nRows before invalid value removal:", rows_before_invalid)
print("Rows after invalid value removal:", len(sold_cleaned))
print("Rows removed:", rows_before_invalid - len(sold_cleaned))

rows_before_missing = len(sold_cleaned)

required_columns = [
    "ClosePrice",
    "CloseDate",
    "ListPrice",
    "LivingArea"
]

existing_required_columns = [
    col for col in required_columns if col in sold_cleaned.columns
]

sold_cleaned = sold_cleaned.dropna(subset=existing_required_columns)

print("\nRows before missing required value removal:", rows_before_missing)
print("Rows after missing required value removal:", len(sold_cleaned))
print("Rows removed:", rows_before_missing - len(sold_cleaned))

for col in ["BedroomsTotal", "BathroomsTotalInteger"]:
    if col in sold_cleaned.columns:
        missing_before = sold_cleaned[col].isnull().sum()
        median_value = sold_cleaned[col].median()
        sold_cleaned[col] = sold_cleaned[col].fillna(median_value)

        print(f"\n{col} missing values filled:", missing_before)
        print(f"{col} median used:", median_value)

if "year_month" in sold_cleaned.columns:
    sold_cleaned = sold_cleaned.drop(columns=["year_month"])

print("\nRemoved unnecessary helper columns")

print("\nRows after Week 4 cleaning:", len(sold_cleaned))
print("Columns after Week 4 cleaning:", len(sold_cleaned.columns))


# ============================================================
# Week 5: Date Consistency and Geographic Data Checks
# ============================================================

print("\n--- Week 5 Date and Geographic Checks ---")

if "ListingContractDate" in sold_cleaned.columns and "CloseDate" in sold_cleaned.columns:
    sold_cleaned["listing_after_close_flag"] = (
        sold_cleaned["ListingContractDate"] > sold_cleaned["CloseDate"]
    )

if "PurchaseContractDate" in sold_cleaned.columns and "CloseDate" in sold_cleaned.columns:
    sold_cleaned["purchase_after_close_flag"] = (
        sold_cleaned["PurchaseContractDate"] > sold_cleaned["CloseDate"]
    )

if "ListingContractDate" in sold_cleaned.columns and "PurchaseContractDate" in sold_cleaned.columns:
    sold_cleaned["negative_timeline_flag"] = (
        sold_cleaned["ListingContractDate"] > sold_cleaned["PurchaseContractDate"]
    )

if "Latitude" in sold_cleaned.columns and "Longitude" in sold_cleaned.columns:
    sold_cleaned["missing_coordinates_flag"] = (
        sold_cleaned["Latitude"].isnull() | sold_cleaned["Longitude"].isnull()
    )

    sold_cleaned["zero_coordinates_flag"] = (
        (sold_cleaned["Latitude"] == 0) | (sold_cleaned["Longitude"] == 0)
    )

    sold_cleaned["positive_longitude_flag"] = (
        sold_cleaned["Longitude"] > 0
    )

    sold_cleaned["implausible_coordinates_flag"] = (
        (sold_cleaned["Latitude"] < 32) |
        (sold_cleaned["Latitude"] > 42) |
        (sold_cleaned["Longitude"] < -125) |
        (sold_cleaned["Longitude"] > -114)
    )

flag_columns = [
    "listing_after_close_flag",
    "purchase_after_close_flag",
    "negative_timeline_flag",
    "missing_coordinates_flag",
    "zero_coordinates_flag",
    "positive_longitude_flag",
    "implausible_coordinates_flag"
]

existing_flag_columns = [
    col for col in flag_columns if col in sold_cleaned.columns
]

print("\nWeek 5 Flag Counts:")
for col in existing_flag_columns:
    print(f"{col}: {sold_cleaned[col].sum()}")

flag_summary = pd.DataFrame({
    "FlagColumn": existing_flag_columns,
    "FlaggedRows": [sold_cleaned[col].sum() for col in existing_flag_columns]
})

flag_summary.to_csv("sold_week5_flag_summary.csv", index=False)

print("\nSaved sold_week5_flag_summary.csv")


# ============================================================
# Final Saved Outputs
# ============================================================

sold.to_csv("sold_combined_residential.csv", index=False)

sold_with_rates.to_csv(
    "sold_with_mortgage_rates.csv",
    index=False
)

sold_cleaned.to_csv(
    "sold_cleaned.csv",
    index=False
)

print("\nSaved sold_combined_residential.csv")
print("Saved sold_with_mortgage_rates.csv")
print("Saved sold_cleaned.csv")