import pandas as pd

# Load the 22jun.csv file
print("Loading 22jun.csv file...")
df = pd.read_csv("22jun.csv", low_memory=False)

# Total number of rows
total_rows = len(df)
print(f"Total number of rows in dataset: {total_rows}")

# Check if LGA column exists
if 'LGA' in df.columns:
    # Count rows with missing LGA
    missing_lga = df['LGA'].isna().sum()
    
    # Calculate percentage
    missing_percentage = (missing_lga / total_rows) * 100
    
    print(f"Number of rows with missing LGA data: {missing_lga} ({missing_percentage:.2f}%)")
    print(f"Number of rows with valid LGA data: {total_rows - missing_lga} ({100 - missing_percentage:.2f}%)")
    
    # Show a few examples of rows with missing LGA
    if missing_lga > 0:
        print("\nExamples of rows with missing LGA:")
        missing_examples = df[df['LGA'].isna()].head(5)
        
        # Show venue name and location for these examples
        for idx, row in missing_examples.iterrows():
            venue_name = row.get('Venue Name', 'Unknown')
            suburb = row.get('Suburb', 'Unknown')
            state = row.get('State', 'Unknown')
            print(f"  • {venue_name} ({suburb}, {state})")
else:
    print("LGA column not found in the dataset")