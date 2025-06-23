import pandas as pd

try:
    # Load the tourism league table
    df = pd.read_csv('tourism_league_table.csv')
    
    # Filter for regions with less than 50 venues
    regions_under_50 = df[df['number_of_venues'] < 50]
    
    if regions_under_50.empty:
        print("No tourism regions have fewer than 50 venues.")
    else:
        print("The following tourism regions have fewer than 50 venues:")
        for index, row in regions_under_50.iterrows():
            print(f"- {row['Tourism Region']}: {int(row['number_of_venues'])} venues")
            
except FileNotFoundError:
    print("The file 'tourism_league_table.csv' was not found.")
    print("Please ensure the league tables have been generated first.")