import pandas as pd

# Load the 22jun.csv file
print("Loading 22jun.csv file...")
df = pd.read_csv("22jun.csv", low_memory=False)

print("\n===== UNIQUE VALUES IN 'Frequency of Music Presentation' =====")

# Check if column exists in the dataframe
if 'Frequency of Music Presentation' in df.columns:
    # Get unique values and count occurrences
    value_counts = df['Frequency of Music Presentation'].value_counts(dropna=False)
    
    print(f"\nFound {len(value_counts)} unique categories:")
    
    # Print each unique value with its count
    for value, count in value_counts.items():
        if pd.isna(value):
            print(f"  • NaN or empty: {count} occurrences")
        else:
            print(f"  • {value}: {count} occurrences")
else:
    print("\nColumn 'Frequency of Music Presentation' not found in 22jun.csv")