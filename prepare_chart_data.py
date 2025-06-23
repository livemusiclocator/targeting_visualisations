import pandas as pd
import numpy as np

# Load the datasets
try:
    revpop_df = pd.read_csv('updated_revpop.csv')
    venues_df = pd.read_csv('22jun.csv')
except FileNotFoundError as e:
    print(f"Error loading CSV file: {e}")
    exit()

# --- Data Cleaning and Preparation ---

# Clean LGA names for consistent merging
revpop_df['LGA_clean'] = revpop_df['LGA Name'].str.replace(' Shire Council| City Council| Rural City Council| Borough Council', '', regex=True).str.strip()
venues_df['LGA_clean'] = venues_df['LGA'].str.replace(' Shire Council| City Council| Rural City Council| Borough Council', '', regex=True).str.strip()

# Clean 'Venue Capacity' - convert to numeric, coercing errors to NaN
venues_df['Venue Capacity'] = pd.to_numeric(venues_df['Venue Capacity'], errors='coerce')

# --- Aggregation ---
# Group by the cleaned LGA name and aggregate the required stats
lga_stats = venues_df.groupby('LGA_clean').agg(
    number_of_venues=('Venue Name', 'nunique'),
    total_capacity=('Venue Capacity', 'sum'),
    avg_capacity=('Venue Capacity', 'mean'),
).reset_index()

# Replace NaN in capacity fields with 0
lga_stats['total_capacity'] = lga_stats['total_capacity'].fillna(0)
lga_stats['avg_capacity'] = lga_stats['avg_capacity'].fillna(0)

# --- Merging ---
# Merge the aggregated stats with the revenue/population data
# Using an inner merge to only include LGAs present in both datasets
combined_df = pd.merge(revpop_df, lga_stats, on='LGA_clean', how='inner')

# Create a 'Council Revenue (Millions)' column for better plotting
combined_df['Council Revenue (Millions)'] = (combined_df['Total Revenue (AUD)'] / 1_000_000).round(2)

# --- Final Column Selection and Saving ---
# Select and rename columns for the final output file
final_cols = {
    'LGA Name': 'lga_name',
    'Council Revenue (Millions)': 'revenue_millions',
    'number_of_venues': 'venue_count',
    'total_capacity': 'total_capacity',
    'avg_capacity': 'avg_capacity'
}
final_df = combined_df[final_cols.keys()].rename(columns=final_cols)

# Round the average capacity for cleaner display
final_df['avg_capacity'] = final_df['avg_capacity'].round(1)

# Save the final prepared data to a new CSV file
output_filename = 'lga_interactive_chart_data.csv'
final_df.to_csv(output_filename, index=False)

print(f"Successfully prepared data and saved to {output_filename}")
print(f"Total LGAs in the final dataset: {len(final_df)}")