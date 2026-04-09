import pandas as pd
import glob

# Getting all sold CSV files
sold_files = glob.glob("CRMLSSold*.csv")

print("Files being combined:")
print(sold_files)

# Load each file
frames = []
for file in sold_files:
    df = pd.read_csv(file, encoding="ISO-8859-1")
    
    # Row count for each individual file before append
    print(f"{file} row count before append: {len(df)}")
    
    frames.append(df)

# Combine all months
sold_combined = pd.concat(frames)

# Row count of the combined/appended dataset after concatenation
print("Rows after concatenation:", len(sold_combined))

# Frequency table of PropertyType before filtering
print("\nPropertyType frequency before filtering:")
print(sold_combined["PropertyType"].value_counts(dropna=False))

# Filter to residential properties
sold_residential = sold_combined[sold_combined["PropertyType"] == "Residential"]

# Row count after applying PropertyType == 'Residential'
print("\nRows after Residential filter:", len(sold_residential))

# Frequency table of PropertyType after filtering
print("\nPropertyType frequency after filtering:")
print(sold_residential["PropertyType"].value_counts(dropna=False))

# Save final dataset
sold_residential.to_csv("sold_combined_residential.csv", index=False)

print("\nSaved sold_combined_residential.csv")