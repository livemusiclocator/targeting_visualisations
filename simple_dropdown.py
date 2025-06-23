import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

# Create a simple HTML file with embedded Plotly and direct controls
html_content = """
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
                <option value="all">-- All LGAs --</option>
                <!-- LGA options will be inserted here -->
                {LGA_OPTIONS}
            </select>
            <div class="highlight-info">Select an LGA to highlight it (others will be dimmed)</div>
        </div>
        <div id="plotly-div" style="width: 100%; height: 800px;"></div>
    </div>

    <script>
        // Data for the plot
        const lgaData = {LGA_DATA};
        const x = {X_DATA};
        const y = {Y_DATA};
        const sizes = {SIZE_DATA};
        const colors = {COLOR_DATA};
        const text = {TEXT_DATA};
        const lgaNames = {LGA_NAMES};
        
        // Create the basic scatter plot
        const trace = {
            x: x,
            y: y,
            mode: 'markers',
            marker: {
                size: sizes,
                color: colors,
                colorscale: 'Viridis',
                colorbar: {
                    title: 'Avg Venue Capacity'
                },
                line: {
                    color: 'darkgray',
                    width: 1
                }
            },
            text: text,
            hoverinfo: 'text',
            type: 'scatter'
        };
        
        // Layout configuration
        const layout = {
            title: 'Interactive Bubble Chart: Number of Venues vs. Average Frequency by LGA<br>Bubble Size = Total Venue Capacity',
            xaxis: {
                title: 'Number of Venues per LGA',
                gridcolor: 'rgba(200, 200, 200, 0.5)'
            },
            yaxis: {
                title: 'Average Frequency of Music Presentation (Gigs per Month)',
                gridcolor: 'rgba(200, 200, 200, 0.5)'
            },
            plot_bgcolor: 'rgba(240, 240, 240, 0.5)',
            hoverlabel: {
                bgcolor: 'white',
                font: {size: 12, family: 'Arial'}
            },
            shapes: [{
                type: 'line',
                x0: 0,
                y0: {AVG_FREQUENCY},
                x1: {MAX_VENUES},
                y1: {AVG_FREQUENCY},
                line: {
                    color: 'red',
                    width: 1,
                    dash: 'dash'
                }
            }],
            annotations: [{
                x: {MAX_VENUES} * 0.98,
                y: {AVG_FREQUENCY} * 1.05,
                text: 'Average frequency: {AVG_FREQUENCY_FORMATTED} gigs/month',
                showarrow: false,
                font: {size: 12, color: 'red'}
            }]
        };
        
        // Initialize the plot
        Plotly.newPlot('plotly-div', [trace], layout);
        
        // Add dropdown functionality
        document.getElementById('lga-select').addEventListener('change', function() {
            const selectedLGA = this.value;
            
            if (selectedLGA === 'all') {
                // Reset all points to full opacity
                Plotly.restyle('plotly-div', {
                    'marker.opacity': 1,
                    'marker.line.color': 'darkgray',
                    'marker.line.width': 1
                });
            } else {
                // Create arrays for opacity and line properties
                const opacity = [];
                const lineColors = [];
                const lineWidths = [];
                
                for (let i = 0; i < lgaNames.length; i++) {
                    if (lgaNames[i] === selectedLGA) {
                        opacity.push(1);  // Full opacity for selected
                        lineColors.push('red');  // Red border
                        lineWidths.push(3);  // Thicker border
                    } else {
                        opacity.push(0.3);  // Dim others
                        lineColors.push('darkgray');  // Normal border
                        lineWidths.push(1);  // Normal width
                    }
                }
                
                // Update the plot
                Plotly.restyle('plotly-div', {
                    'marker.opacity': [opacity],
                    'marker.line.color': [lineColors],
                    'marker.line.width': [lineWidths]
                });
            }
        });
    </script>
</body>
</html>
"""

# Sort LGAs alphabetically for the dropdown
sorted_lga_stats = filtered_lga_stats.sort_values('LGA').reset_index(drop=True)

# Generate HTML options for the dropdown
lga_options = '\n'.join([f'<option value="{lga}">{lga}</option>' for lga in sorted_lga_stats['LGA']])

# Convert data to JSON-safe formats (avoiding numpy arrays)
x_data = sorted_lga_stats['Venue Count'].tolist()
y_data = sorted_lga_stats['Avg Frequency'].tolist()
size_data = (sorted_lga_stats['Total Capacity'] / 100).tolist()
color_data = sorted_lga_stats['Avg Capacity'].tolist()
text_data = sorted_lga_stats['hover_text'].tolist()
lga_names = sorted_lga_stats['LGA'].tolist()
avg_frequency = float(sorted_lga_stats['Avg Frequency'].mean())
max_venues = float(sorted_lga_stats['Venue Count'].max()) * 1.05

# Replace placeholders in the HTML template
html_content = html_content.replace('{LGA_OPTIONS}', lga_options)
html_content = html_content.replace('{LGA_DATA}', str(lga_names))
html_content = html_content.replace('{X_DATA}', str(x_data))
html_content = html_content.replace('{Y_DATA}', str(y_data))
html_content = html_content.replace('{SIZE_DATA}', str(size_data))
html_content = html_content.replace('{COLOR_DATA}', str(color_data))
html_content = html_content.replace('{TEXT_DATA}', str(text_data))
html_content = html_content.replace('{LGA_NAMES}', str(lga_names))
html_content = html_content.replace('{AVG_FREQUENCY}', str(avg_frequency))
html_content = html_content.replace('{AVG_FREQUENCY_FORMATTED}', f"{avg_frequency:.2f}")
html_content = html_content.replace('{MAX_VENUES}', str(max_venues))

# Write to file
with open('lga_interactive_dropdown.html', 'w') as f:
    f.write(html_content)

print("Created interactive visualization with dropdown: lga_interactive_dropdown.html")
print("\nOpen the HTML file in a web browser to use the interactive visualization with working dropdown.")