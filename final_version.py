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

# Sort alphabetically for the dropdown
sorted_lgas = sorted(filtered_lga_stats['LGA'])

# Create an HTML file with the final version combining all features
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
            background-color: #f0f0ff;
            border-radius: 8px;
            border: 2px solid #ccccff;
        }
        select {
            padding: 8px;
            border-radius: 4px;
            border: 1px solid #aaa;
            font-size: 14px;
            min-width: 300px;
            background-color: #fff;
        }
        label {
            font-weight: bold;
            margin-right: 10px;
            font-size: 16px;
        }
        .highlight-info {
            font-style: italic;
            margin-top: 10px;
            color: #555;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        button {
            padding: 8px 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-left: 10px;
        }
        button:hover {
            background-color: #45a049;
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
                {LGA_OPTIONS}
            </select>
            <button id="highlight-btn">Highlight Selected LGA</button>
            <div class="highlight-info">
                When an LGA is selected, it will be highlighted with a bright red bubble while others are dimmed.
                Hover over any bubble to see detailed information.
            </div>
        </div>
        <div id="chart" style="width: 100%; height: 800px;"></div>
    </div>

    <script>
        // Data for the plot
        const lgas = {LGA_LIST};
        const venueCount = {VENUE_COUNT};
        const avgFreq = {AVG_FREQ};
        const totalCapacity = {TOTAL_CAPACITY};
        const avgCapacity = {AVG_CAPACITY};
        const freqMode = {FREQ_MODE};
        const avgFrequencyLine = {AVG_FREQUENCY_LINE};
        
        // Create the data with custom hover text
        function createHoverText(i) {
            return `<b>${lgas[i]}</b><br>` +
                   `Venues: ${venueCount[i]}<br>` +
                   `Most common frequency: ${freqMode[i]}<br>` +
                   `Avg frequency: ${avgFreq[i].toFixed(2)} gigs/month<br>` +
                   `Total capacity: ${Math.round(totalCapacity[i])}<br>` +
                   `Avg capacity: ${Math.round(avgCapacity[i])}`;
        }
        
        // Calculate bubble sizes based on total capacity
        function calculateSizes(capacities, scaleFactor = 0.25, minSize = 5) {
            return capacities.map(cap => Math.max(Math.sqrt(cap) * scaleFactor, minSize));
        }
        
        // Function to create the plot with all LGAs
        function createPlot() {
            const hoverTexts = [];
            for (let i = 0; i < lgas.length; i++) {
                hoverTexts.push(createHoverText(i));
            }
            
            // Calculate sizes based on total capacity
            const bubbleSizes = calculateSizes(totalCapacity);
            
            const trace = {
                x: venueCount,
                y: avgFreq,
                mode: 'markers',
                type: 'scatter',
                text: hoverTexts,
                hoverinfo: 'text',
                marker: {
                    size: bubbleSizes,
                    color: avgCapacity,
                    colorscale: 'Viridis',
                    colorbar: {
                        title: 'Avg Venue<br>Capacity'
                    },
                    line: {
                        width: 1,
                        color: 'darkgray'
                    }
                }
            };
            
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
                    font: {
                        family: 'Arial',
                        size: 12
                    },
                    bordercolor: 'gray'
                },
                shapes: [{
                    type: 'line',
                    x0: 0,
                    y0: avgFrequencyLine,
                    x1: Math.max(...venueCount) * 1.05,
                    y1: avgFrequencyLine,
                    line: {
                        color: 'red',
                        width: 1,
                        dash: 'dash'
                    }
                }],
                annotations: [{
                    x: Math.max(...venueCount) * 0.95,
                    y: avgFrequencyLine * 1.05,
                    text: `Average frequency: ${avgFrequencyLine.toFixed(2)} gigs/month`,
                    showarrow: false,
                    font: {
                        color: 'red'
                    }
                }]
            };
            
            Plotly.newPlot('chart', [trace], layout);
        }
        
        // Function to highlight a specific LGA
        function highlightLGA(selectedLGA) {
            if (selectedLGA === 'all') {
                // Show all LGAs normally
                createPlot();
                return;
            }
            
            // Find the index of the selected LGA
            const lgaIndex = lgas.indexOf(selectedLGA);
            if (lgaIndex === -1) return;
            
            // Create hover texts
            const hoverTexts = [];
            const highlightHoverText = createHoverText(lgaIndex);
            
            for (let i = 0; i < lgas.length; i++) {
                hoverTexts.push(createHoverText(i));
            }
            
            // Calculate sizes based on total capacity, but make highlighted one larger
            const regularSizes = calculateSizes(totalCapacity);
            const highlightedSizes = [...regularSizes];
            highlightedSizes[lgaIndex] = Math.max(regularSizes[lgaIndex] * 1.5, 15); // Make highlighted bubble larger
            
            // Create a trace for all LGAs
            const trace = {
                x: venueCount,
                y: avgFreq,
                mode: 'markers',
                type: 'scatter',
                text: hoverTexts,
                hoverinfo: 'text',
                marker: {
                    size: highlightedSizes,
                    color: Array(lgas.length).fill('rgba(100, 100, 100, 0.3)'), // All dimmed
                    line: {
                        width: Array(lgas.length).fill(1),
                        color: Array(lgas.length).fill('darkgray')
                    }
                }
            };
            
            // Override properties for the highlighted LGA
            trace.marker.color[lgaIndex] = 'rgba(255, 0, 0, 1)'; // Bright red
            trace.marker.line.width[lgaIndex] = 3;
            trace.marker.line.color[lgaIndex] = 'black';
            
            const layout = {
                title: `Interactive Bubble Chart: ${selectedLGA} Highlighted<br>Bubble Size = Total Venue Capacity`,
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
                    font: {
                        family: 'Arial',
                        size: 12
                    },
                    bordercolor: 'gray'
                },
                shapes: [{
                    type: 'line',
                    x0: 0,
                    y0: avgFrequencyLine,
                    x1: Math.max(...venueCount) * 1.05,
                    y1: avgFrequencyLine,
                    line: {
                        color: 'red',
                        width: 1,
                        dash: 'dash'
                    }
                }],
                annotations: [{
                    x: Math.max(...venueCount) * 0.95,
                    y: avgFrequencyLine * 1.05,
                    text: `Average frequency: ${avgFrequencyLine.toFixed(2)} gigs/month`,
                    showarrow: false,
                    font: {
                        color: 'red'
                    }
                }]
            };
            
            Plotly.newPlot('chart', [trace], layout);
        }
        
        // Initialize the plot
        createPlot();
        
        // Handle the highlight button click
        document.getElementById('highlight-btn').addEventListener('click', function() {
            const selectedLGA = document.getElementById('lga-select').value;
            highlightLGA(selectedLGA);
        });
        
        // Also highlight when selecting from dropdown
        document.getElementById('lga-select').addEventListener('change', function() {
            const selectedLGA = this.value;
            highlightLGA(selectedLGA);
        });
    </script>
</body>
</html>
"""

# Generate the dropdown options
lga_options = "\n                ".join([f'<option value="{lga}">{lga}</option>' for lga in sorted_lgas])

# Replace placeholders with actual data
html_content = html_content.replace("{LGA_OPTIONS}", lga_options)
html_content = html_content.replace("{LGA_LIST}", str(filtered_lga_stats['LGA'].tolist()))
html_content = html_content.replace("{VENUE_COUNT}", str(filtered_lga_stats['Venue Count'].tolist()))
html_content = html_content.replace("{AVG_FREQ}", str(filtered_lga_stats['Avg Frequency'].tolist()))
html_content = html_content.replace("{TOTAL_CAPACITY}", str(filtered_lga_stats['Total Capacity'].tolist()))
html_content = html_content.replace("{AVG_CAPACITY}", str(filtered_lga_stats['Avg Capacity'].tolist()))
html_content = html_content.replace("{FREQ_MODE}", str(filtered_lga_stats['Frequency Mode'].tolist()))
html_content = html_content.replace("{AVG_FREQUENCY_LINE}", str(filtered_lga_stats['Avg Frequency'].mean()))

# Write to file
with open('lga_final_version.html', 'w') as f:
    f.write(html_content)

print("Created final version HTML file: lga_final_version.html")
print("\nOpen the HTML file in a web browser to see the visualization with:")
print("1. Proper highlighting of only one LGA at a time")
print("2. Hover information for all bubbles")
print("3. Bubble sizes scaled by total venue capacity")