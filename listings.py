

import pandas as pd
import glob

# ============================================================
# Week 1: Load, Combine, and Filter Listing Data
# ============================================================

listing_files = glob.glob("CRMLSListing*.csv")

print("Files being combined:")
print(listing_files)

frames = []

for file in listing_files:
    df = pd.read_csv(file, encoding="ISO-8859-1", low_memory=False)
    print(f"{file} row count before append: {len(df)}")
    frames.append(df)

listed = pd.concat(frames, ignore_index=True)

print("\nRows after concatenation:", len(listed))

print("\nPropertyType frequency before filtering:")
print(listed["PropertyType"].value_counts(dropna=False))

listed = listed[listed["PropertyType"] == "Residential"]

print("\nRows after Residential filter:", len(listed))

print("\nPropertyType frequency after filtering:")
print(listed["PropertyType"].value_counts(dropna=False))


# ============================================================
# Week 2: Dataset Checks, Null Analysis, and Summary Statistics
# ============================================================

print("\nDataset shape:")
print(listed.shape)

print("\nColumn names:")
print(listed.columns)

print("\nData types:")
print(listed.dtypes)

print("\nFirst 5 rows:")
print(listed.head())

print("\nUnique PropertyType Values:")
print(listed["PropertyType"].unique())

print("\nNull count by column:")
null_counts = listed.isnull().sum()
print(null_counts)

print("\nMissing percentage by column:")
missing_percent = (listed.isnull().sum() / len(listed)) * 100
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

null_summary.to_csv("listed_null_summary.csv", index=True)

print("\nSaved listed_null_summary.csv")

numeric_columns = [
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "DaysOnMarket"
]

for column in numeric_columns:
    if column in listed.columns:
        print(f"\nSummary statistics for {column}:")
        print(listed[column].describe())

print("\nMedian ListPrice:", listed["ListPrice"].median())
print("Average ListPrice:", listed["ListPrice"].mean())

if "OriginalListPrice" in listed.columns:
    print("\nPercentage of listings with price drop:")
    print((listed["ListPrice"] < listed["OriginalListPrice"]).mean() * 100)


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

listed["year_month"] = pd.to_datetime(
    listed["ListingContractDate"],
    errors="coerce"
).dt.to_period("M")

listed_with_rates = listed.merge(
    mortgage_monthly,
    on="year_month",
    how="left"
)

print("\nMissing mortgage rates in listed data:")
print(listed_with_rates["rate_30yr_fixed"].isnull().sum())

print("\nListed preview with mortgage rates:")
print(
    listed_with_rates[
        [
            "ListingContractDate",
            "year_month",
            "ListPrice",
            "rate_30yr_fixed"
        ]
    ].head()
)


# ============================================================
# Week 4: Basic Data Cleaning
# ============================================================

listed_cleaned = listed_with_rates.copy()

print("\n--- Week 4 Cleaning ---")
print("Rows before cleaning:", len(listed_cleaned))
print("Columns before cleaning:", len(listed_cleaned.columns))

date_columns = [
    "ListingContractDate",
    "PurchaseContractDate",
    "CloseDate",
    "ContractStatusChangeDate"
]

for col in date_columns:
    if col in listed_cleaned.columns:
        listed_cleaned[col] = pd.to_datetime(
            listed_cleaned[col],
            errors="coerce"
        )

print("\nDate columns converted")

numeric_columns = [
    "ListPrice",
    "OriginalListPrice",
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "Latitude",
    "Longitude",
    "rate_30yr_fixed"
]

for col in numeric_columns:
    if col in listed_cleaned.columns:
        listed_cleaned[col] = pd.to_numeric(
            listed_cleaned[col],
            errors="coerce"
        )

print("Numeric columns converted")


# ============================================================
# Remove unnecessary and redundant columns
# ============================================================

cols_to_drop = [

    # Duplicate columns
    "PropertyType.1",
    "DaysOnMarket.1",
    "LivingArea.1",
    "Longitude.1",
    "Latitude.1",
    "ListPrice.1",
    "CloseDate.1",
    "BuyerOfficeName.1",
    "UnparsedAddress.1",

    # Agent/person fields
    "ListAgentEmail",
    "ListAgentFirstName",
    "ListAgentLastName",
    "ListAgentFullName",
    "CoListAgentFirstName",
    "CoListAgentLastName",
    "BuyerAgentFirstName",
    "BuyerAgentLastName",
    "BuyerAgentMlsId",
    "CoBuyerAgentFirstName",

    # Compensation fields
    "BuyerAgencyCompensation",
    "BuyerAgencyCompensationType",

    # Redundant identifiers
    "ListingKeyNumeric",
    "ListingId",
    "StreetNumberNumeric",

    # Extremely sparse or low-value fields
    "BuilderName",
    "BusinessType",
    "BelowGradeFinishedArea",
    "AboveGradeFinishedArea",
    "TaxAnnualAmount",
    "TaxYear",
    "CoveredSpaces",
    "LotSizeDimensions",

    # Helper column from mortgage merge
    "year_month"
]

cols_to_drop = [
    col for col in cols_to_drop
    if col in listed_cleaned.columns
]

print("\nColumns before unnecessary/redundant column removal:",
      len(listed_cleaned.columns))

listed_cleaned = listed_cleaned.drop(columns=cols_to_drop)

print("Columns after unnecessary/redundant column removal:",
      len(listed_cleaned.columns))

print("Columns removed:",
      len(cols_to_drop))

print("\nDropped columns:")
print(cols_to_drop)


# ============================================================
# Remove remaining columns with more than 90% missing values
# ============================================================

missing_percent_cleaned = (
    listed_cleaned.isnull().mean() * 100
)

high_missing_cols = missing_percent_cleaned[
    missing_percent_cleaned > 90
].index.tolist()

high_missing_cols = [
    col for col in high_missing_cols
    if col in listed_cleaned.columns
]

print("\nColumns before high-missing column removal:",
      len(listed_cleaned.columns))

listed_cleaned = listed_cleaned.drop(
    columns=high_missing_cols
)

print("\nDropped high-missing columns (>90% missing):")
print(high_missing_cols)

print("Columns after high-missing column removal:",
      len(listed_cleaned.columns))


# ============================================================
# Remove invalid numeric values
# ============================================================

rows_before_invalid = len(listed_cleaned)

if "ListPrice" in listed_cleaned.columns:
    listed_cleaned = listed_cleaned[listed_cleaned["ListPrice"] > 0]

if "LivingArea" in listed_cleaned.columns:
    listed_cleaned = listed_cleaned[listed_cleaned["LivingArea"] > 0]

if "DaysOnMarket" in listed_cleaned.columns:
    listed_cleaned = listed_cleaned[listed_cleaned["DaysOnMarket"] >= 0]

if "BedroomsTotal" in listed_cleaned.columns:
    listed_cleaned = listed_cleaned[listed_cleaned["BedroomsTotal"] >= 0]

if "BathroomsTotalInteger" in listed_cleaned.columns:
    listed_cleaned = listed_cleaned[listed_cleaned["BathroomsTotalInteger"] >= 0]

print("\nRows before invalid value removal:", rows_before_invalid)
print("Rows after invalid value removal:", len(listed_cleaned))
print("Rows removed:", rows_before_invalid - len(listed_cleaned))

rows_before_missing = len(listed_cleaned)

required_columns = [
    "ListPrice",
    "ListingContractDate",
    "LivingArea"
]

existing_required_columns = [
    col for col in required_columns if col in listed_cleaned.columns
]

listed_cleaned = listed_cleaned.dropna(subset=existing_required_columns)

print("\nRows before missing required value removal:", rows_before_missing)
print("Rows after missing required value removal:", len(listed_cleaned))
print("Rows removed:", rows_before_missing - len(listed_cleaned))

for col in ["BedroomsTotal", "BathroomsTotalInteger"]:
    if col in listed_cleaned.columns:
        missing_before = listed_cleaned[col].isnull().sum()
        median_value = listed_cleaned[col].median()
        listed_cleaned[col] = listed_cleaned[col].fillna(median_value)

        print(f"\n{col} missing values filled:", missing_before)
        print(f"{col} median used:", median_value)

print("\nRows after Week 4 cleaning:", len(listed_cleaned))
print("Columns after Week 4 cleaning:", len(listed_cleaned.columns))


# ============================================================
# Week 5: Date Consistency and Geographic Data Checks
# ============================================================

print("\n--- Week 5 Date and Geographic Checks ---")

if "ListingContractDate" in listed_cleaned.columns and "CloseDate" in listed_cleaned.columns:
    listed_cleaned["listing_after_close_flag"] = (
        listed_cleaned["ListingContractDate"] > listed_cleaned["CloseDate"]
    )

if "PurchaseContractDate" in listed_cleaned.columns and "CloseDate" in listed_cleaned.columns:
    listed_cleaned["purchase_after_close_flag"] = (
        listed_cleaned["PurchaseContractDate"] > listed_cleaned["CloseDate"]
    )

if "ListingContractDate" in listed_cleaned.columns and "PurchaseContractDate" in listed_cleaned.columns:
    listed_cleaned["negative_timeline_flag"] = (
        listed_cleaned["ListingContractDate"] > listed_cleaned["PurchaseContractDate"]
    )

if "Latitude" in listed_cleaned.columns and "Longitude" in listed_cleaned.columns:
    listed_cleaned["missing_coordinates_flag"] = (
        listed_cleaned["Latitude"].isnull() | listed_cleaned["Longitude"].isnull()
    )

    listed_cleaned["zero_coordinates_flag"] = (
        (listed_cleaned["Latitude"] == 0) | (listed_cleaned["Longitude"] == 0)
    )

    listed_cleaned["positive_longitude_flag"] = (
        listed_cleaned["Longitude"] > 0
    )

    listed_cleaned["implausible_coordinates_flag"] = (
        (listed_cleaned["Latitude"] < 32) |
        (listed_cleaned["Latitude"] > 42) |
        (listed_cleaned["Longitude"] < -125) |
        (listed_cleaned["Longitude"] > -114)
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
    col for col in flag_columns if col in listed_cleaned.columns
]

print("\nWeek 5 Flag Counts:")
for col in existing_flag_columns:
    print(f"{col}: {listed_cleaned[col].sum()}")

flag_summary = pd.DataFrame({
    "FlagColumn": existing_flag_columns,
    "FlaggedRows": [listed_cleaned[col].sum() for col in existing_flag_columns]
})

flag_summary.to_csv("listed_week5_flag_summary.csv", index=False)

print("\nSaved listed_week5_flag_summary.csv")


# ============================================================
# Week 6: Feature Engineering and Market Metrics
# ============================================================

print("\n--- Week 6 Feature Engineering ---")

# Listing datasets may not have ClosePrice for every row because not every
# listing is closed. These metrics will only calculate when the needed data exists.

if "ClosePrice" in listed_cleaned.columns and "OriginalListPrice" in listed_cleaned.columns:
    listed_cleaned["price_ratio"] = (
        listed_cleaned["ClosePrice"] /
        listed_cleaned["OriginalListPrice"]
    )

if "ClosePrice" in listed_cleaned.columns and "LivingArea" in listed_cleaned.columns:
    listed_cleaned["price_per_sqft"] = (
        listed_cleaned["ClosePrice"] /
        listed_cleaned["LivingArea"]
    )

if "ClosePrice" in listed_cleaned.columns and "OriginalListPrice" in listed_cleaned.columns:
    listed_cleaned["close_to_original_list_ratio"] = (
        listed_cleaned["ClosePrice"] /
        listed_cleaned["OriginalListPrice"]
    )

if (
    "PurchaseContractDate" in listed_cleaned.columns and
    "ListingContractDate" in listed_cleaned.columns
):
    listed_cleaned["listing_to_contract_days"] = (
        listed_cleaned["PurchaseContractDate"] -
        listed_cleaned["ListingContractDate"]
    ).dt.days

if (
    "CloseDate" in listed_cleaned.columns and
    "PurchaseContractDate" in listed_cleaned.columns
):
    listed_cleaned["contract_to_close_days"] = (
        listed_cleaned["CloseDate"] -
        listed_cleaned["PurchaseContractDate"]
    ).dt.days

if "ListingContractDate" in listed_cleaned.columns:
    listed_cleaned["year_month"] = (
        listed_cleaned["ListingContractDate"]
        .dt.to_period("M")
    )

print("\nWeek 6 metrics created")

week6_columns = [
    "price_ratio",
    "price_per_sqft",
    "close_to_original_list_ratio",
    "listing_to_contract_days",
    "contract_to_close_days"
]

existing_week6_columns = [
    col for col in week6_columns
    if col in listed_cleaned.columns
]

print("\nWeek 6 metric summary statistics:")
print(
    listed_cleaned[existing_week6_columns]
    .describe()
)


# ============================================================
# Week 6: Segment Analysis
# ============================================================

print("\n--- Week 6 Segment Analysis ---")

segment_fields = [
    "PropertyType",
    "PropertySubType",
    "CountyOrParish",
    "MLSAreaMajor"
]

for segment in segment_fields:
    if segment in listed_cleaned.columns:
        print(f"\nSegment summary by {segment}:")

        summary_metrics = {}

        if "ListPrice" in listed_cleaned.columns:
            summary_metrics["ListPrice"] = ["count", "mean", "median"]

        if "DaysOnMarket" in listed_cleaned.columns:
            summary_metrics["DaysOnMarket"] = ["mean", "median"]

        if "LivingArea" in listed_cleaned.columns:
            summary_metrics["LivingArea"] = ["mean", "median"]

        if summary_metrics:
            segment_summary = listed_cleaned.groupby(segment).agg(summary_metrics)

            print(segment_summary.head(10))

            output_file = f"listed_segment_summary_by_{segment}.csv"
            segment_summary.to_csv(output_file)

            print(f"Saved {output_file}")


# ============================================================
# Final Saved Outputs
# ============================================================

listed.to_csv("listed_combined_residential.csv", index=False)

listed_with_rates.to_csv(
    "listed_with_mortgage_rates.csv",
    index=False
)

listed_cleaned.to_csv(
    "listed_cleaned.csv",
    index=False
)

listed_cleaned.to_csv(
    "listed_week6_metrics.csv",
    index=False
)

print("\nSaved listed_combined_residential.csv")
print("Saved listed_with_mortgage_rates.csv")
print("Saved listed_cleaned.csv")
print("Saved listed_week6_metrics.csv")
