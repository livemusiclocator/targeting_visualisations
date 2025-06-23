import pandas as pd
import numpy as np

# Load the 22jun.csv file
print("Loading 22jun.csv file...")
df = pd.read_csv("22jun.csv", low_memory=False)

# Check if both columns exist in the dataframe
if 'Frequency of Music Presentation' in df.columns and 'Presentation Classification' in df.columns:
    print("\n===== CORRELATION BETWEEN FREQUENCY AND CLASSIFICATION =====")
    
    # Create a cross-tabulation of the two columns
    cross_tab = pd.crosstab(
        df['Frequency of Music Presentation'], 
        df['Presentation Classification'],
        margins=True,
        margins_name='Total'
    )
    
    # Display the cross-tabulation
    print("\nCross-tabulation of Frequency and Classification:")
    print(cross_tab)
    
    # For each Frequency category, show the corresponding Classification categories
    print("\n===== MAPPING BETWEEN FREQUENCY AND CLASSIFICATION =====")
    
    for freq in sorted(df['Frequency of Music Presentation'].dropna().unique()):
        # Filter to just rows with this frequency
        subset = df[df['Frequency of Music Presentation'] == freq]
        
        # Count occurrences of each classification
        class_counts = subset['Presentation Classification'].value_counts()
        
        print(f"\nFrequency: '{freq}' ({len(subset)} venues)")
        for classification, count in class_counts.items():
            percentage = (count / len(subset)) * 100
            print(f"  • {classification}: {count} venues ({percentage:.1f}%)")
            
else:
    if 'Frequency of Music Presentation' not in df.columns:
        print("\nColumn 'Frequency of Music Presentation' not found in 22jun.csv")
    if 'Presentation Classification' not in df.columns:
        print("\nColumn 'Presentation Classification' not found in 22jun.csv")