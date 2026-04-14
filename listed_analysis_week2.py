
import pandas as pd 

# Load the filtered listed dataset 
listed = pd.read_csv("listed_combined_residential.csv", encoding="ISO-8859-1")

# Inspect structure
print("Dataset shape:")
print(listed.shape)

print("\nColumn names:")
print(listed.columns)

print("\nData types:")
print(listed.dtypes)

print("\nFirst 5 rows:")
print(listed.head())

# Check unique property types 
print("\nUnique PropertyType Values:")
print(listed["PropertyType"].unique())

# Validate null counts 
print("\nNull count by column:")
null_counts = listed.isnull().sum()
print(null_counts)

# Missing value percentages
print("\nMissing percentage by column:")
missing_percent = (listed.isnull().sum() / len(listed)) * 100
print(missing_percent)

# Columns with more than 90% missing values
print("\nColumns with more than 90% missing values:")
high_missing = missing_percent[missing_percent > 90]
print(high_missing)

# Identify columns that may be dropped due to very high missing values
print("\nSuggested columns to drop (>90% missing):")
print(high_missing.index.tolist())

# Summary statistics for required numeric columns
numeric_columns = ["ClosePrice", "ListPrice", "LivingArea", "DaysOnMarket"]

for column in numeric_columns:
    print(f"\nSummary statistics for {column}:")
    print(listed[column].describe())

# Save null summary table
null_summary = pd.DataFrame({"NullCount": null_counts, "MissingPercent": missing_percent})

null_summary.to_csv("listed_null_summary.csv", index=True)

print("\nSaved listed_null_summary.csv")

# Check listing price statistics
print("\nMedian ListPrice:", listed["ListPrice"].median())
print("Average ListPrice:", listed["ListPrice"].mean())

# Compare original vs current list price (price drops)
if "OriginalListPrice" in listed.columns:
    print("\nPercentage of listings with price drop:")
    print((listed["ListPrice"] < listed["OriginalListPrice"]).mean() * 100)