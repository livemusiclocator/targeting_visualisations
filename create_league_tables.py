import pandas as pd
import numpy as np

# Load the datasets
try:
    revpop_df = pd.read_csv('updated_revpop.csv')
    venues_df = pd.read_csv('22jun.csv')
except FileNotFoundError as e:
    print(f"Error loading CSV file: {e}")
    exit()

# Function to estimate gigs per week from frequency text
def estimate_gigs(frequency):
    frequency = str(frequency).lower()
    if '2 or more a week' in frequency:
        return 2.5
    elif '1 or more a week' in frequency:
        return 1.5
    elif '3 or more a week' in frequency:
        return 3.5
    elif 'less than once a week' in frequency:
        return 0.5
    elif 'nil' in frequency:
        return 0
    else:
        return 0 # Default for unhandled cases

# Apply the gig estimation to the venues dataframe
venues_df['estimated_gigs'] = venues_df['Frequency of Music Presentation'].apply(estimate_gigs)

# LGA League Table
# Group by LGA and aggregate
lga_stats = venues_df.groupby('LGA').agg(
    number_of_venues=('Venue Name', 'nunique'),
    number_of_gigs=('estimated_gigs', 'sum')
).reset_index()

# Merge with revenue and population data
# First, clean up LGA names to ensure consistent merging
revpop_df['LGA Name'] = revpop_df['LGA Name'].str.replace(' Shire Council', '').str.replace(' City Council', '').str.replace(' Rural City Council', '').str.strip()
lga_stats['LGA'] = lga_stats['LGA'].str.replace(' Shire Council', '').str.replace(' City Council', '').str.replace(' Rural City Council', '').str.strip()

lga_league_table = pd.merge(revpop_df, lga_stats, left_on='LGA Name', right_on='LGA', how='left')

# Drop the redundant LGA column from the merge, rename and select columns for the final LGA table
lga_league_table = lga_league_table.drop(columns=['LGA'])
lga_league_table = lga_league_table.rename(columns={'LGA Name': 'LGA', 'Total Revenue (AUD)': 'Council Revenue'})
lga_league_table = lga_league_table[['LGA', 'Council Revenue', 'number_of_venues', 'number_of_gigs']]
lga_league_table = lga_league_table.fillna(0) # Fill NaN with 0 for venues/gigs in LGAs with no listed venues

# Tourism Region League Table
tourism_stats = venues_df.groupby('Tourism Area').agg(
    number_of_venues=('Venue Name', 'nunique'),
    number_of_gigs=('estimated_gigs', 'sum')
).reset_index()

# Rename columns for the final tourism table
tourism_league_table = tourism_stats.rename(columns={'Tourism Area': 'Tourism Region'})

# Save the league tables to new CSV files
lga_league_table.to_csv('lga_league_table.csv', index=False)
tourism_league_table.to_csv('tourism_league_table.csv', index=False)

# Print the tables to the console
print("--- LGA League Table ---")
print(lga_league_table)
print("\n--- Tourism Region League Table ---")
print(tourism_league_table)

print("\nLeague tables saved to lga_league_table.csv and tourism_league_table.csv")