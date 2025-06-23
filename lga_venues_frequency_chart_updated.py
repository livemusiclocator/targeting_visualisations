import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the 22jun.csv file
print("Loading 22jun.csv file...")
df = pd.read_csv("22jun.csv", low_memory=False)

# Clean the data
print(f"Original dataset: {len(df)} rows")

# Remove completely empty rows
df_clean = df.dropna(how='all')
print(f"After removing empty rows: {len(df_clean)} rows")

# Drop rows with missing LGA
df_clean = df_clean.dropna(subset=['LGA'])
print(f"After removing rows with missing LGA: {len(df_clean)} rows")

# Create a function to convert frequency to numeric value for plotting
def frequency_to_numeric(freq):
    if pd.isna(freq) or freq == 'No Data':
        return 0
    elif freq == 'Less than 1 a month':
        return 0.2
    elif freq == 'Hosts functions':
        return 0.5
    elif freq == '1 or more a month':
        return 1
    elif freq == '2 or more a month':
        return 2
    elif freq == '3 or more a month':
        return 3
    elif freq == '1 or more a week':
        return 4
    elif freq == '2 or more a week':
        return 8
    elif freq == '3 or more a week':
        return 12
    elif freq == '4 or more a week':
        return 16
    elif freq == '5 or more a week':
        return 20
    elif freq == '6 or more a week':
        return 24
    else:
        return 0

# Add numeric frequency column
df_clean['Numeric Frequency'] = df_clean['Frequency of Music Presentation'].apply(frequency_to_numeric)

# Convert venue capacity to numeric, handling non-numeric values
df_clean['Venue Capacity'] = pd.to_numeric(df_clean['Venue Capacity'], errors='coerce')
df_clean['Venue Capacity'] = df_clean['Venue Capacity'].fillna(0)

# Group by LGA
lga_stats = df_clean.groupby('LGA').agg({
    'Venue Name': 'count',  # Count of venues
    'Numeric Frequency': 'mean',  # Average frequency
    'Venue Capacity': ['sum', 'mean']  # Total and average capacity
}).reset_index()

# Rename columns for clarity
lga_stats.columns = ['LGA', 'Venue Count', 'Avg Frequency', 'Total Capacity', 'Avg Capacity']

# Find the mode of frequency for each LGA
frequency_modes = {}
for lga in df_clean['LGA'].unique():
    lga_data = df_clean[df_clean['LGA'] == lga]
    mode_series = lga_data['Frequency of Music Presentation'].mode()
    frequency_modes[lga] = mode_series.iloc[0] if not mode_series.empty else 'No Data'

# Add the frequency mode to the stats dataframe
lga_stats['Frequency Mode'] = lga_stats['LGA'].map(frequency_modes)

# Filter to LGAs with at least 5 venues for better visualization
filtered_lga_stats = lga_stats[lga_stats['Venue Count'] >= 5].copy()
print(f"LGAs with at least 5 venues: {len(filtered_lga_stats)}")

# Sort by venue count
filtered_lga_stats = filtered_lga_stats.sort_values('Venue Count', ascending=False)

# Create bubble chart
plt.figure(figsize=(16, 10))

# Create scatter plot
scatter = plt.scatter(
    filtered_lga_stats['Venue Count'], 
    filtered_lga_stats['Avg Frequency'],
    s=filtered_lga_stats['Total Capacity'] / 100,  # Scale bubble size
    alpha=0.6,
    c=filtered_lga_stats['Avg Capacity'],  # Color by average capacity
    cmap='viridis'
)

# Add colorbar
cbar = plt.colorbar()
cbar.set_label('Average Venue Capacity')

# Add labels for the largest bubbles (by venue count and by total capacity)
for i, row in filtered_lga_stats.nlargest(10, 'Venue Count').iterrows():
    plt.annotate(
        row['LGA'],
        xy=(row['Venue Count'], row['Avg Frequency']),
        xytext=(5, 0),
        textcoords='offset points',
        fontsize=9,
        ha='left'
    )

# Also label LGAs with highest average frequency
for i, row in filtered_lga_stats.nlargest(5, 'Avg Frequency').iterrows():
    if row['LGA'] not in filtered_lga_stats.nlargest(10, 'Venue Count')['LGA'].values:
        plt.annotate(
            row['LGA'],
            xy=(row['Venue Count'], row['Avg Frequency']),
            xytext=(5, 0),
            textcoords='offset points',
            fontsize=9,
            ha='left',
            color='red'
        )

# Set labels and title
plt.xlabel('Number of Venues per LGA')
plt.ylabel('Average Frequency of Music Presentation (Gigs per Month)')
plt.title('Bubble Chart: Number of Venues vs. Average Frequency by LGA\nBubble Size = Total Venue Capacity')

# Add grid
plt.grid(True, linestyle='--', alpha=0.7)

# Save the chart
plt.tight_layout()
plt.savefig('lga_venues_frequency_chart.png', dpi=300)
print("Chart saved as lga_venues_frequency_chart.png")

# Show the chart
plt.show()

# Print top LGAs by venue count
print("\nTop 10 LGAs by venue count:")
print(filtered_lga_stats[['LGA', 'Venue Count', 'Frequency Mode', 'Avg Frequency', 'Total Capacity']].head(10).to_string(index=False))

# Print LGAs with highest average frequency
print("\nTop 10 LGAs by average frequency (with at least 5 venues):")
print(filtered_lga_stats.sort_values('Avg Frequency', ascending=False)[['LGA', 'Venue Count', 'Frequency Mode', 'Avg Frequency', 'Total Capacity']].head(10).to_string(index=False))

# Create a CSV with all the LGA statistics
lga_stats.to_csv('lga_music_venue_statistics.csv', index=False)
print("\nDetailed statistics saved to lga_music_venue_statistics.csv")