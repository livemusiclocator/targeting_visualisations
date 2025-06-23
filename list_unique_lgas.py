import pandas as pd

# Load the 22jun.csv file
print("Loading 22jun.csv file...")
df = pd.read_csv("22jun.csv", low_memory=False)

# Clean the data by removing completely empty rows
df_clean = df.dropna(how='all')

# Get unique LGAs and sort them alphabetically
unique_lgas = sorted(df_clean['LGA'].dropna().unique())

# Print the total count
print(f"\nTotal number of unique LGAs: {len(unique_lgas)}")

# Print the list of unique LGAs
print("\nList of unique LGAs in the dataset:")
for i, lga in enumerate(unique_lgas, 1):
    print(f"{i}. {lga}")

# Also save to a text file
with open('unique_lgas.txt', 'w') as f:
    f.write(f"Total number of unique LGAs: {len(unique_lgas)}\n\n")
    f.write("List of unique LGAs in the dataset:\n")
    for i, lga in enumerate(unique_lgas, 1):
        f.write(f"{i}. {lga}\n")

print("\nList saved to unique_lgas.txt")