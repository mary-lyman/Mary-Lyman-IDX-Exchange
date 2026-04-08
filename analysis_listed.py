
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
    frames.append(df)

# Combine all months
listing_combined = pd.concat(frames)

# Row count check
print("Rows after concatenation:", len(listing_combined))

# Filter to residential properties
listing_residential = listing_combined[listing_combined["PropertyType"] == "Residential"]

print("Rows after Residential filter:", len(listing_residential))

# Save final dataset
listing_residential.to_csv("listed_combined_residential.csv", index=False)

print("Saved listed_combined_residential.csv")