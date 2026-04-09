import pandas as pd
import glob

# Get all listing CSV files
listing_files = glob.glob("CRMLSListing*.csv")

print("Files being combined:")
print(listing_files)

# Load each file
frames = []
for file in listing_files:
    df = pd.read_csv(file, encoding="ISO-8859-1")
    
    # Row count for each individual file before append
    print(f"{file} row count before append: {len(df)}")
    
    frames.append(df)

# Combine all months
listing_combined = pd.concat(frames)

# Row count of the combined dataset after concatenation
print("Rows after concatenation:", len(listing_combined))

# Frequency table of PropertyType before filtering
print("\nPropertyType frequency before filtering:")
print(listing_combined["PropertyType"].value_counts(dropna=False))

# Filter to residential properties
listing_residential = listing_combined[listing_combined["PropertyType"] == "Residential"]

# Row count after applying filter
print("\nRows after Residential filter:", len(listing_residential))

# Frequency table after filtering
print("\nPropertyType frequency after filtering:")
print(listing_residential["PropertyType"].value_counts(dropna=False))

# Save final dataset
listing_residential.to_csv("listed_combined_residential.csv", index=False)

print("\nSaved listed_combined_residential.csv")
