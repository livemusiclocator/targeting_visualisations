import pandas as pd

# Load the 22jun.csv file
print("Loading 22jun.csv file...")
df = pd.read_csv("22jun.csv", low_memory=False)

print("\n===== UNIQUE VALUES IN 'Presentation Classification' =====")

# Check if column exists in the dataframe
if 'Presentation Classification' in df.columns:
    # Get unique values and count occurrences
    value_counts = df['Presentation Classification'].value_counts(dropna=False)
    
    print(f"\nFound {len(value_counts)} unique categories:")
    
    # Print each unique value with its count
    for value, count in value_counts.items():
        if pd.isna(value):
            print(f"  • NaN or empty: {count} occurrences")
        else:
            print(f"  • {value}: {count} occurrences")
else:
    print("\nColumn 'Presentation Classification' not found in 22jun.csv")