import pandas as pd
import numpy as np

print("Loading 22jun.csv file...")
df = pd.read_csv("22jun.csv", low_memory=False)

# Get the specific row with missing LGA
missing_lga_row = df[df['LGA'].isna()]

if len(missing_lga_row) == 0:
    print("No rows with missing LGA found")
    exit(0)

# Get the index of the row with missing LGA
missing_idx = missing_lga_row.index[0]
print(f"Row with missing LGA is at index {missing_idx} (row {missing_idx + 1} in the CSV file)")

# Check if this row has any data at all
non_null_count = missing_lga_row.iloc[0].count()
if non_null_count == 0:
    print("This row is completely empty (all values are null)")
else:
    # Display non-null values
    print(f"This row has {non_null_count} non-null values:")
    for col, val in missing_lga_row.iloc[0].items():
        if not pd.isna(val):
            print(f"  • {col}: {val}")

# Try to identify the venue
venue_name = missing_lga_row.iloc[0].get('Venue Name', None)
if pd.isna(venue_name):
    print("\nVenue name is missing (null)")
else:
    print(f"\nVenue name: {venue_name}")

# Display some context: rows before and after
context_rows = 2  # Number of rows before and after to show
start_idx = max(0, missing_idx - context_rows)
end_idx = min(len(df) - 1, missing_idx + context_rows)

print(f"\nShowing rows {start_idx + 1} to {end_idx + 1} for context:")
context_df = df.iloc[start_idx:end_idx + 1]

# Display key columns for identification
key_columns = ['Source', 'Venue Name', 'Suburb', 'State', 'LGA']
available_columns = [col for col in key_columns if col in df.columns]

for idx, row in context_df.iterrows():
    venue = row.get('Venue Name', 'Unknown')
    source = row.get('Source', 'Unknown')
    suburb = row.get('Suburb', 'Unknown')
    state = row.get('State', 'Unknown')
    lga = row.get('LGA', 'Unknown')
    
    if idx == missing_idx:
        print(f"Row {idx + 1} (MISSING LGA): Source={source}, Venue={venue}, Location={suburb}, {state}, LGA={lga}")
    else:
        print(f"Row {idx + 1}: Source={source}, Venue={venue}, Location={suburb}, {state}, LGA={lga}")