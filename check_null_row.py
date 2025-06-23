import pandas as pd
import numpy as np

print("Loading 22jun.csv file...")
df = pd.read_csv("22jun.csv", low_memory=False)

# Identify row with missing LGA
missing_lga_row = df[df['LGA'].isna()]

if len(missing_lga_row) == 0:
    print("No rows with missing LGA found")
    exit(0)

print(f"Found {len(missing_lga_row)} row(s) with missing LGA")

# For each row with missing LGA, check if it has any non-null values
for idx, row in missing_lga_row.iterrows():
    print(f"\nAnalyzing row {idx}:")
    
    # Count non-null values
    non_null_count = row.count()
    total_columns = len(row)
    null_percentage = (1 - non_null_count / total_columns) * 100
    
    print(f"Non-null values: {non_null_count} out of {total_columns} columns ({null_percentage:.2f}% null)")
    
    # Check if there are any non-null values, and if so, show them
    if non_null_count > 0:
        print("Non-null values in this row:")
        for col, val in row.items():
            if not pd.isna(val):
                print(f"  • {col}: {val}")
    else:
        print("This row is completely empty (all values are null)")

# Create a clean version without completely empty rows
if non_null_count == 0:
    clean_df = df.dropna(how='all')
    
    # Verify the number of rows removed
    rows_removed = len(df) - len(clean_df)
    print(f"\nRemoved {rows_removed} completely empty row(s)")
    
    # Save the clean version
    clean_df.to_csv("22jun_clean.csv", index=False)
    print("Saved cleaned file to 22jun_clean.csv")