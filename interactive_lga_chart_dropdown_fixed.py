import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

# Filter to LGAs with at least 3 venues for better visualization
filtered_lga_stats = lga_stats[lga_stats['Venue Count'] >= 3].copy()
print(f"LGAs with at least 3 venues: {len(filtered_lga_stats)}")

# Sort alphabetically for the dropdown
sorted_lga_stats = filtered_lga_stats.sort_values('LGA').reset_index(drop=True)

# Add additional text for hover information
sorted_lga_stats['Hover Text'] = sorted_lga_stats.apply(
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

# Create a figure
fig = go.Figure()

# Add a scatter trace for all LGAs (this will be our base/complete view)
fig.add_trace(go.Scatter(
    x=sorted_lga_stats['Venue Count'],
    y=sorted_lga_stats['Avg Frequency'],
    mode='markers',
    marker=dict(
        size=sorted_lga_stats['Total Capacity'] / 100,  # Scale bubble size
        sizemin=5,
        sizemode='area',
        sizeref=2.*max(sorted_lga_stats['Total Capacity'])/(100**2),
        color=sorted_lga_stats['Avg Capacity'],
        colorscale='Viridis',
        colorbar=dict(title='Avg Venue Capacity'),
        line=dict(width=1, color='DarkSlateGrey')
    ),
    text=sorted_lga_stats['Hover Text'],
    hoverinfo='text',
    name='All LGAs'
))

# Add a scatter trace for each LGA (these will be shown/hidden by dropdown)
for i, lga in enumerate(sorted_lga_stats['LGA']):
    lga_data = sorted_lga_stats[sorted_lga_stats['LGA'] == lga]
    
    fig.add_trace(go.Scatter(
        x=lga_data['Venue Count'],
        y=lga_data['Avg Frequency'],
        mode='markers',
        marker=dict(
            size=lga_data['Total Capacity'] / 100,  # Scale bubble size
            sizemin=10,  # Minimum size a bit larger for the highlighted points
            sizemode='area',
            sizeref=2.*max(sorted_lga_stats['Total Capacity'])/(100**2),
            color=lga_data['Avg Capacity'],
            colorscale='Viridis',
            line=dict(width=2, color='red')  # Highlighted with red border
        ),
        text=lga_data['Hover Text'],
        hoverinfo='text',
        name=lga,
        visible=False  # Start with these traces hidden
    ))

# Create buttons for dropdown
buttons = [dict(
    label='All LGAs',
    method='update',
    args=[{'visible': [True] + [False] * len(sorted_lga_stats)}]  # Only show the first trace (all LGAs)
)]

for i, lga in enumerate(sorted_lga_stats['LGA']):
    # For each LGA, create a button that shows only that LGA and the base layer
    visibility = [True]  # Keep the base layer visible
    visibility.extend([False] * len(sorted_lga_stats))  # Hide all individual LGA traces
    visibility[i+1] = True  # Show only the selected LGA trace
    
    buttons.append(dict(
        label=lga,
        method='update',
        args=[{'visible': visibility}]
    ))

# Add dropdown menu to the figure
fig.update_layout(
    updatemenus=[
        dict(
            active=0,
            buttons=buttons,
            direction="down",
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.1,
            xanchor="left",
            y=1.15,
            yanchor="top",
            font=dict(size=12),
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='rgba(0, 0, 0, 0.4)',
            borderwidth=1
        ),
    ],
    annotations=[
        dict(text="Select LGA:", x=0.005, y=1.14, xref="paper", yref="paper",
             align="left", showarrow=False, font=dict(size=14, family="Arial"))
    ]
)

# Add a line showing the average frequency across all LGAs
avg_freq = sorted_lga_stats['Avg Frequency'].mean()
fig.add_shape(
    type="line",
    x0=0,
    y0=avg_freq,
    x1=sorted_lga_stats['Venue Count'].max() * 1.05,
    y1=avg_freq,
    line=dict(
        color="red",
        width=1,
        dash="dash",
    )
)
fig.add_annotation(
    x=sorted_lga_stats['Venue Count'].max() * 0.98,
    y=avg_freq * 1.05,
    text=f"Average frequency: {avg_freq:.2f} gigs/month",
    showarrow=False,
    font=dict(size=12, color="red")
)

# Update layout
fig.update_layout(
    xaxis_title='Number of Venues per LGA',
    yaxis_title='Average Frequency of Music Presentation (Gigs per Month)',
    title={
        'text': 'Interactive Bubble Chart: Number of Venues vs. Average Frequency by LGA<br>Bubble Size = Total Venue Capacity',
        'x': 0.5,
        'xanchor': 'center'
    },
    width=1100,
    height=800,
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
output_file = 'lga_venues_frequency_interactive_with_working_dropdown.html'
fig.write_html(output_file)
print(f"Interactive chart with working dropdown saved as {output_file}")

# Also save as a static image for reference
fig.write_image('lga_venues_frequency_interactive_with_working_dropdown.png', scale=2)
print("Static version saved as lga_venues_frequency_interactive_with_working_dropdown.png")

# Print top LGAs by venue count
print("\nTop 10 LGAs by venue count:")
print(sorted_lga_stats.sort_values('Venue Count', ascending=False)[['LGA', 'Venue Count', 'Frequency Mode', 'Avg Frequency', 'Total Capacity']].head(10).to_string(index=False))

# Print LGAs with highest average frequency
print("\nTop 10 LGAs by average frequency (with at least 3 venues):")
print(sorted_lga_stats.sort_values('Avg Frequency', ascending=False)[['LGA', 'Venue Count', 'Frequency Mode', 'Avg Frequency', 'Total Capacity']].head(10).to_string(index=False))

print("\nTo view the interactive chart with working LGA selection dropdown, open the HTML file in a web browser.")