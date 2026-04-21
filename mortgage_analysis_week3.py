

import pandas as pd

# Load mortgage rate data from FRED
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url)

print("Mortgage columns:")
print(mortgage.columns)

# Rename columns
mortgage.columns = ["date", "rate_30yr_fixed"]

# Convert date column to datetime
mortgage["date"] = pd.to_datetime(mortgage["date"], errors="coerce")

# Convert weekly mortgage data to monthly averages
mortgage["year_month"] = mortgage["date"].dt.to_period("M")
mortgage_monthly = mortgage.groupby("year_month")["rate_30yr_fixed"].mean().reset_index()

# Load datasets
sold = pd.read_csv("sold_combined_residential.csv", encoding="ISO-8859-1", low_memory=False)
listed = pd.read_csv("listed_combined_residential.csv", encoding="ISO-8859-1", low_memory=False)

# Create matching month key
sold["year_month"] = pd.to_datetime(sold["CloseDate"], errors="coerce").dt.to_period("M")
listed["year_month"] = pd.to_datetime(listed["ListingContractDate"], errors="coerce").dt.to_period("M")

# Merge mortgage rates onto each dataset
sold_with_rates = sold.merge(mortgage_monthly, on="year_month", how="left")
listed_with_rates = listed.merge(mortgage_monthly, on="year_month", how="left")

# Check for missing mortgage rates after merge
print("Missing mortgage rates in sold data:")
print(sold_with_rates["rate_30yr_fixed"].isnull().sum())

print("\nMissing mortgage rates in listed data:")
print(listed_with_rates["rate_30yr_fixed"].isnull().sum())

# Preview merged data
print("\nSold preview:")
print(sold_with_rates[["CloseDate", "year_month", "ClosePrice", "rate_30yr_fixed"]].head())

print("\nListed preview:")
print(listed_with_rates[["ListingContractDate", "year_month", "ListPrice", "rate_30yr_fixed"]].head())

# Save new files
sold_with_rates.to_csv("sold_with_mortgage_rates.csv", index=False)
listed_with_rates.to_csv("listed_with_mortgage_rates.csv", index=False)

print("\nFiles saved successfully.")