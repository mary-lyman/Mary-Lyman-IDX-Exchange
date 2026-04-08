
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
    frames.append(df)

# Combine all months
sold_combined = pd.concat(frames)

# Show row count after combining
print("Rows after concatenation:", len(sold_combined))

# Filter to residential properties
sold_residential = sold_combined[sold_combined["PropertyType"] == "Residential"]

print("Rows after Residential filter:", len(sold_residential))

# Save final dataset
sold_residential.to_csv("sold_combined_residential.csv", index=False)

print("Saved sold_combined_residential.csv")