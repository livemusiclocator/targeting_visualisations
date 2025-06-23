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

# Filter to LGAs with at least 3 venues for better visualization
filtered_lga_stats = lga_stats[lga_stats['Venue Count'] >= 3].copy()
print(f"LGAs with at least 3 venues: {len(filtered_lga_stats)}")

# Add hover text for better information display
filtered_lga_stats['hover_text'] = filtered_lga_stats.apply(
    lambda row: f"<b>{row['LGA']}</b><br>" +
                f"Venues: {row['Venue Count']}<br>" +
                f"Frequency Mode: {row['Frequency Mode']}<br>" +
                f"Avg Frequency: {row['Avg Frequency']:.2f} gigs/month<br>" +
                f"Total Capacity: {int(row['Total Capacity'])}<br>" +
                f"Avg Capacity: {int(row['Avg Capacity'])}",
    axis=1
)

# Use Plotly Express for the initial plot - this is much simpler
fig = px.scatter(
    filtered_lga_stats,
    x='Venue Count',
    y='Avg Frequency',
    size='Total Capacity',
    color='Avg Capacity',
    hover_name='LGA',
    hover_data={
        'LGA': False,  # Hide in hover, using hover_name instead
        'Venue Count': True,
        'Avg Frequency': ':.2f',
        'Frequency Mode': True,
        'Total Capacity': True,
        'Avg Capacity': ':.0f',
        'hover_text': False  # We'll use this for custom hover
    },
    color_continuous_scale='Viridis',
    labels={
        'Venue Count': 'Number of Venues',
        'Avg Frequency': 'Average Gigs per Month',
        'Avg Capacity': 'Average Venue Capacity'
    },
    title='Music Venues by LGA',
)

# Customize hover template
fig.update_traces(
    hovertemplate='%{customdata[5]}<extra></extra>',
    customdata=filtered_lga_stats[['LGA', 'Venue Count', 'Avg Frequency', 'Frequency Mode', 
                                  'Total Capacity', 'Avg Capacity', 'hover_text']]
)

# Update layout for better appearance
fig.update_layout(
    title='Interactive LGA Music Venue Analysis<br>Bubble Size = Total Capacity',
    xaxis_title='Number of Venues per LGA',
    yaxis_title='Average Frequency (Gigs per Month)',
    coloraxis_colorbar_title='Avg Venue<br>Capacity',
    width=1100,
    height=800,
    plot_bgcolor='rgba(240, 240, 240, 0.5)',
    hoverlabel=dict(
        bgcolor="white",
        font_size=12,
        font_family="Arial"
    ),
)

# Create a different HTML file that uses HTML+JavaScript to create the dropdown
# This is a more reliable approach than trying to use Plotly's built-in dropdown
html_output = """
<!DOCTYPE html>
<html>
<head>
    <title>LGA Music Venue Analysis</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .controls {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #eef;
            border-radius: 8px;
        }
        select {
            padding: 8px;
            border-radius: 4px;
            border: 1px solid #ccc;
            font-size: 14px;
            min-width: 300px;
        }
        label {
            font-weight: bold;
            margin-right: 10px;
        }
        .highlight-info {
            font-style: italic;
            margin-top: 10px;
            color: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Interactive LGA Music Venue Analysis</h1>
        <div class="controls">
            <label for="lga-select">Select LGA to Highlight:</label>
            <select id="lga-select">
                <option value="">-- All LGAs --</option>
                <!-- LGA options will be inserted here by JavaScript -->
            </select>
            <div class="highlight-info">Selected LGA will be highlighted with a red border</div>
        </div>
        <div id="chart"></div>
    </div>

    <script>
        // Load the Plotly figure data
        const figureData = PLOT_DATA_PLACEHOLDER;
        
        // LGA names array
        const lgaNames = LGA_NAMES_PLACEHOLDER;
        
        // Populate the dropdown with LGA options
        const dropdown = document.getElementById('lga-select');
        lgaNames.forEach(lga => {
            const option = document.createElement('option');
            option.value = lga;
            option.textContent = lga;
            dropdown.appendChild(option);
        });
        
        // Function to highlight selected LGA
        function highlightLGA(selectedLGA) {
            // Start with original marker settings
            const updatedTraces = JSON.parse(JSON.stringify(figureData.data));
            
            // If an LGA is selected, update marker properties
            if (selectedLGA) {
                // Get customdata which contains LGA names
                updatedTraces[0].marker.line = {
                    width: [],
                    color: []
                };
                
                // Loop through each point
                for (let i = 0; i < updatedTraces[0].customdata.length; i++) {
                    const lga = updatedTraces[0].customdata[i][0]; // LGA name is first in customdata
                    
                    if (lga === selectedLGA) {
                        // Highlight selected LGA
                        updatedTraces[0].marker.line.width[i] = 3;
                        updatedTraces[0].marker.line.color[i] = 'red';
                    } else {
                        // Other LGAs get a thin line
                        updatedTraces[0].marker.line.width[i] = 1;
                        updatedTraces[0].marker.line.color[i] = 'darkgray';
                        
                        // Dim other points
                        if (!updatedTraces[0].marker.opacity) {
                            updatedTraces[0].marker.opacity = [];
                            for (let j = 0; j < updatedTraces[0].customdata.length; j++) {
                                updatedTraces[0].marker.opacity[j] = 1;
                            }
                        }
                        updatedTraces[0].marker.opacity[i] = 0.3;
                    }
                }
            }
            
            // Update the plot
            Plotly.react('chart', updatedTraces, figureData.layout);
        }
        
        // Add event listener for dropdown changes
        dropdown.addEventListener('change', function() {
            highlightLGA(this.value);
        });
        
        // Initial plot
        Plotly.newPlot('chart', figureData.data, figureData.layout);
    </script>
</body>
</html>
"""

# Convert the Plotly figure to JSON for embedding in HTML
import json
figure_json = json.dumps(fig.to_dict())
lga_names_json = json.dumps(sorted(filtered_lga_stats['LGA'].tolist()))

# Replace placeholders in the HTML template
html_output = html_output.replace('PLOT_DATA_PLACEHOLDER', figure_json)
html_output = html_output.replace('LGA_NAMES_PLACEHOLDER', lga_names_json)

# Write to file
with open('lga_interactive_with_html_dropdown.html', 'w') as f:
    f.write(html_output)

print("Created HTML file with interactive dropdown: lga_interactive_with_html_dropdown.html")

# Create a static version for reference
fig.write_image('lga_interactive_static.png', scale=2)
print("Static image saved as lga_interactive_static.png")

print("\nOpen the HTML file in a web browser to use the interactive visualization with working dropdown.")