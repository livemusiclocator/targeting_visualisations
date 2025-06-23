import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the 22jun.csv file
print("Loading 22jun.csv file...")
df = pd.read_csv("22jun.csv", low_memory=False)

# Check necessary columns exist
required_columns = ['LGA', 'Frequency of Music Presentation', 'Venue Capacity']
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    print(f"Missing required columns: {missing_columns}")
    exit(1)

# Drop rows with missing LGA
df = df.dropna(subset=['LGA'])

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
df['Numeric Frequency'] = df['Frequency of Music Presentation'].apply(frequency_to_numeric)

# Group by LGA
lga_groups = df.groupby('LGA')

# Calculate metrics for each LGA
lga_data = []
for lga, group in lga_groups:
    # Count venues
    venue_count = len(group)
    
    # Calculate mode of frequency (most common frequency)
    frequency_mode = group['Frequency of Music Presentation'].mode().iloc[0] if not group['Frequency of Music Presentation'].mode().empty else 'No Data'
    numeric_frequency_mode = frequency_to_numeric(frequency_mode)
    
    # Calculate average frequency
    avg_frequency = group['Numeric Frequency'].mean()
    
    # Calculate total capacity
    total_capacity = group['Venue Capacity'].sum()
    
    # Calculate average capacity
    avg_capacity = group['Venue Capacity'].mean()
    
    lga_data.append({
        'LGA': lga,
        'Venue Count': venue_count,
        'Frequency Mode': frequency_mode,
        'Numeric Frequency Mode': numeric_frequency_mode,
        'Avg Numeric Frequency': avg_frequency,
        'Total Capacity': total_capacity,
        'Avg Capacity': avg_capacity
    })

# Convert to DataFrame
lga_df = pd.DataFrame(lga_data)

# Sort by venue count
lga_df = lga_df.sort_values('Venue Count', ascending=False)

# Filter to LGAs with at least 5 venues for better visualization
filtered_lga_df = lga_df[lga_df['Venue Count'] >= 5]

# Create bubble chart
plt.figure(figsize=(16, 10))

# Create scatter plot
scatter = plt.scatter(
    filtered_lga_df['Venue Count'], 
    filtered_lga_df['Avg Numeric Frequency'],
    s=filtered_lga_df['Total Capacity'] / 100,  # Scale bubble size
    alpha=0.6,
    c=filtered_lga_df['Avg Capacity'],  # Color by average capacity
    cmap='viridis'
)

# Add colorbar
cbar = plt.colorbar()
cbar.set_label('Average Venue Capacity')

# Add labels for the largest bubbles
for i, row in filtered_lga_df.nlargest(15, 'Venue Count').iterrows():
    plt.annotate(
        row['LGA'],
        xy=(row['Venue Count'], row['Avg Numeric Frequency']),
        xytext=(5, 0),
        textcoords='offset points',
        fontsize=9,
        ha='left'
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
print(lga_df[['LGA', 'Venue Count', 'Frequency Mode', 'Avg Numeric Frequency', 'Total Capacity']].head(10).to_string(index=False))

# Print LGAs with highest average frequency
print("\nTop 10 LGAs by average frequency:")
print(lga_df.sort_values('Avg Numeric Frequency', ascending=False)[['LGA', 'Venue Count', 'Frequency Mode', 'Avg Numeric Frequency', 'Total Capacity']].head(10).to_string(index=False))