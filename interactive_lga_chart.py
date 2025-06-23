import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

# Count venues by state to show in hover text
state_counts = {}
for lga in filtered_lga_stats['LGA']:
    # Get the venues in this LGA
    venues_in_lga = df_clean[df_clean['LGA'] == lga]
    
    # Count venues by state
    if 'State' in venues_in_lga.columns:
        state_counts[lga] = venues_in_lga['State'].value_counts().to_dict()
    else:
        state_counts[lga] = {'Unknown': len(venues_in_lga)}

# Add additional text for hover information
filtered_lga_stats['Hover Text'] = filtered_lga_stats.apply(
    lambda row: (
        f"<b>{row['LGA']}</b><br>" +
        f"Venues: {row['Venue Count']}<br>" +
        f"Most common frequency: {row['Frequency Mode']}<br>" +
        f"Avg frequency: {row['Avg Frequency']:.1f} gigs/month<br>" +
        f"Total capacity: {int(row['Total Capacity'])}<br>" +
        f"Avg capacity: {int(row['Avg Capacity'])}"
    ),
    axis=1
)

# Create interactive bubble chart with Plotly
fig = px.scatter(
    filtered_lga_stats, 
    x='Venue Count',
    y='Avg Frequency',
    size='Total Capacity',
    color='Avg Capacity',
    hover_name='LGA',
    hover_data={
        'Venue Count': True,
        'Avg Frequency': ':.2f',
        'Total Capacity': True,
        'Avg Capacity': True,
        'Frequency Mode': True,
        'LGA': False,  # Hide this as we're using hover_name
        'Hover Text': False  # Hide this as we'll use custom hovertemplate
    },
    color_continuous_scale='viridis',
    size_max=50,
    opacity=0.7,
    title='Interactive Bubble Chart: Number of Venues vs. Average Frequency by LGA'
)

# Customize hover template
fig.update_traces(
    hovertemplate='%{hovertext}<extra></extra>',
    hovertext=filtered_lga_stats['Hover Text']
)

# Update layout
fig.update_layout(
    xaxis_title='Number of Venues per LGA',
    yaxis_title='Average Frequency of Music Presentation (Gigs per Month)',
    coloraxis_colorbar_title='Avg Venue Capacity',
    title={
        'text': 'Interactive Bubble Chart: Number of Venues vs. Average Frequency by LGA<br>Bubble Size = Total Venue Capacity',
        'x': 0.5,
        'xanchor': 'center'
    },
    width=1000,
    height=700,
    plot_bgcolor='rgba(240, 240, 240, 0.5)',  # Light gray background
    hoverlabel=dict(
        bgcolor="white",
        font_size=12,
        font_family="Arial"
    ),
)

# Add grid
fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200, 200, 200, 0.5)')
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200, 200, 200, 0.5)')

# Save as interactive HTML
output_file = 'lga_venues_frequency_interactive.html'
fig.write_html(output_file)
print(f"Interactive chart saved as {output_file}")

# Also save as a static image for reference
fig.write_image('lga_venues_frequency_interactive.png', scale=2)
print("Static version saved as lga_venues_frequency_interactive.png")

# Print top LGAs by venue count
print("\nTop 10 LGAs by venue count:")
print(filtered_lga_stats[['LGA', 'Venue Count', 'Frequency Mode', 'Avg Frequency', 'Total Capacity']].head(10).to_string(index=False))

# Print LGAs with highest average frequency
print("\nTop 10 LGAs by average frequency (with at least 5 venues):")
print(filtered_lga_stats.sort_values('Avg Frequency', ascending=False)[['LGA', 'Venue Count', 'Frequency Mode', 'Avg Frequency', 'Total Capacity']].head(10).to_string(index=False))

# Create a CSV with all the LGA statistics
lga_stats.to_csv('lga_music_venue_statistics.csv', index=False)
print("\nDetailed statistics saved to lga_music_venue_statistics.csv")

print("\nTo view the interactive chart, open the HTML file in a web browser.")