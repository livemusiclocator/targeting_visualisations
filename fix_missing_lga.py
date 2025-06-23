import pandas as pd
import numpy as np

print("Loading CSV files...")
oct_df = pd.read_csv("7oct.csv", low_memory=False)
jun_df = pd.read_csv("22jun.csv", low_memory=False)

# Identify row with missing LGA in 22jun.csv
missing_lga_row = jun_df[jun_df['LGA'].isna()]

if len(missing_lga_row) == 0:
    print("No rows with missing LGA found in 22jun.csv")
    exit(0)

print(f"Found {len(missing_lga_row)} row(s) with missing LGA in 22jun.csv")

# Check which coordinate columns exist in both datasets
coordinate_cols_jun = [col for col in jun_df.columns if col in ['Lat', 'Long', 'GLat', 'GLong', 'Geocode Latitude', 'Geocode Longitude']]
coordinate_cols_oct = [col for col in oct_df.columns if col in ['Lat', 'Long', 'Latitude', 'Longitude']]

print(f"Coordinate columns in 22jun.csv: {coordinate_cols_jun}")
print(f"Coordinate columns in 7oct.csv: {coordinate_cols_oct}")

# Process each row with missing LGA
for idx, row in missing_lga_row.iterrows():
    print(f"\nProcessing row {idx}:")
    
    # Try to show venue name and basic info for identification
    venue_name = row.get('Venue Name', 'Unknown')
    suburb = row.get('Suburb', 'Unknown')
    state = row.get('State', 'Unknown')
    print(f"Venue: {venue_name} ({suburb}, {state})")
    
    # Get coordinates from 22jun.csv
    coordinates_found = False
    lat_jun = None
    long_jun = None
    
    # Try different coordinate columns
    if 'Lat' in jun_df.columns and 'Long' in jun_df.columns:
        lat_jun = row.get('Lat')
        long_jun = row.get('Long')
        if not (pd.isna(lat_jun) or pd.isna(long_jun)):
            coordinates_found = True
            print(f"Found coordinates in Lat/Long: {lat_jun}, {long_jun}")
    
    if not coordinates_found and 'GLat' in jun_df.columns and 'GLong' in jun_df.columns:
        lat_jun = row.get('GLat')
        long_jun = row.get('GLong')
        if not (pd.isna(lat_jun) or pd.isna(long_jun)):
            coordinates_found = True
            print(f"Found coordinates in GLat/GLong: {lat_jun}, {long_jun}")
    
    if not coordinates_found and 'Geocode Latitude' in jun_df.columns and 'Geocode Longitude' in jun_df.columns:
        lat_jun = row.get('Geocode Latitude')
        long_jun = row.get('Geocode Longitude')
        if not (pd.isna(lat_jun) or pd.isna(long_jun)):
            coordinates_found = True
            print(f"Found coordinates in Geocode Latitude/Longitude: {lat_jun}, {long_jun}")
    
    if not coordinates_found:
        print("No valid coordinates found in 22jun.csv row")
        continue
    
    # Search for matching coordinates in 7oct.csv
    matches = []
    if 'Lat' in oct_df.columns and 'Long' in oct_df.columns:
        # Find exact match
        exact_matches = oct_df[(oct_df['Lat'] == lat_jun) & (oct_df['Long'] == long_jun)]
        if len(exact_matches) > 0:
            matches.extend(exact_matches.to_dict('records'))
            print(f"Found {len(exact_matches)} exact match(es) in Lat/Long")
        
        # Find approximate matches within small radius
        if len(matches) == 0:
            tolerance = 0.001  # Approximately 100 meters
            approx_matches = oct_df[
                (oct_df['Lat'] >= lat_jun - tolerance) & 
                (oct_df['Lat'] <= lat_jun + tolerance) & 
                (oct_df['Long'] >= long_jun - tolerance) & 
                (oct_df['Long'] <= long_jun + tolerance)
            ]
            
            if len(approx_matches) > 0:
                matches.extend(approx_matches.to_dict('records'))
                print(f"Found {len(approx_matches)} approximate match(es) within {tolerance} degrees")
    
    # Also try with Latitude/Longitude columns if they exist
    if len(matches) == 0 and 'Latitude' in oct_df.columns and 'Longitude' in oct_df.columns:
        # Find exact match
        exact_matches = oct_df[(oct_df['Latitude'] == lat_jun) & (oct_df['Longitude'] == long_jun)]
        if len(exact_matches) > 0:
            matches.extend(exact_matches.to_dict('records'))
            print(f"Found {len(exact_matches)} exact match(es) in Latitude/Longitude")
        
        # Find approximate matches within small radius
        if len(matches) == 0:
            tolerance = 0.001  # Approximately 100 meters
            approx_matches = oct_df[
                (oct_df['Latitude'] >= lat_jun - tolerance) & 
                (oct_df['Latitude'] <= lat_jun + tolerance) & 
                (oct_df['Longitude'] >= long_jun - tolerance) & 
                (oct_df['Longitude'] <= long_jun + tolerance)
            ]
            
            if len(approx_matches) > 0:
                matches.extend(approx_matches.to_dict('records'))
                print(f"Found {len(approx_matches)} approximate match(es) within {tolerance} degrees")
    
    # If no matches found by coordinates, try by venue name
    if len(matches) == 0 and not pd.isna(venue_name):
        # Clean venue name for better matching
        clean_name = venue_name.replace("'", "").strip()
        name_matches = oct_df[oct_df['Venue Name'].str.contains(clean_name, case=False, na=False)]
        
        if len(name_matches) > 0:
            matches.extend(name_matches.to_dict('records'))
            print(f"Found {len(name_matches)} match(es) by venue name")
    
    # Process matches
    if len(matches) == 0:
        print("No matches found in 7oct.csv")
        continue
    
    # If multiple matches, use the first one
    match = matches[0]
    lga_oct = match.get('LGA')
    
    if pd.isna(lga_oct):
        print("Match found but LGA is also missing in 7oct.csv")
        continue
    
    print(f"Found LGA in 7oct.csv: {lga_oct}")
    
    # Update the LGA in 22jun.csv
    jun_df.at[idx, 'LGA'] = lga_oct
    print(f"Updated LGA for row {idx} to: {lga_oct}")

# Save the updated file
jun_df.to_csv("22jun_updated.csv", index=False)
print("\nSaved updated file to 22jun_updated.csv")

# Count rows with missing LGA in the updated file
missing_lga_after = jun_df['LGA'].isna().sum()
print(f"Rows with missing LGA after update: {missing_lga_after}")