import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Load both datasets
print("Loading datasets...")
revenue_df = pd.read_csv("updated_revpop.csv")
venues_df = pd.read_csv("22jun.csv", low_memory=False)

print(f"Revenue dataset: {len(revenue_df)} rows")
print(f"Venues dataset: {len(venues_df)} rows")

# Clean venues dataset
venues_df = venues_df.dropna(how='all')
venues_df = venues_df.dropna(subset=['LGA'])

# Create a function to convert frequency to numeric value
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

# Add numeric frequency column to venues dataset
venues_df['Numeric Frequency'] = venues_df['Frequency of Music Presentation'].apply(frequency_to_numeric)

# Convert venue capacity to numeric
venues_df['Venue Capacity'] = pd.to_numeric(venues_df['Venue Capacity'], errors='coerce')
venues_df['Venue Capacity'] = venues_df['Venue Capacity'].fillna(0)

# Aggregate venue data by LGA
venue_stats = venues_df.groupby('LGA').agg({
    'Venue Name': 'count',  # Count of venues
    'Numeric Frequency': 'mean',  # Average frequency
    'Venue Capacity': ['sum', 'mean']  # Total and average capacity
}).reset_index()

# Rename columns for clarity
venue_stats.columns = ['LGA', 'Venue Count', 'Avg Frequency', 'Total Capacity', 'Avg Capacity']

# Format the LGA names in the revenue dataset to match venue dataset
revenue_df['LGA'] = revenue_df['LGA Name']

# Merge the datasets
merged_df = pd.merge(venue_stats, revenue_df, on='LGA', how='inner')
print(f"Merged dataset has {len(merged_df)} rows")

# Show the number of LGAs in each dataset that didn't match
venues_only = set(venue_stats['LGA']) - set(revenue_df['LGA'])
revenue_only = set(revenue_df['LGA']) - set(venue_stats['LGA'])
print(f"LGAs in venue data only: {len(venues_only)}")
print(f"LGAs in revenue data only: {len(revenue_only)}")

if len(venues_only) > 0:
    print("Sample LGAs in venue data only:", list(venues_only)[:5])
if len(revenue_only) > 0:
    print("Sample LGAs in revenue data only:", list(revenue_only)[:5])

# Calculate gig density metrics
merged_df['Venues Per 10k Population'] = (merged_df['Venue Count'] / merged_df['Population']) * 10000
merged_df['Total Capacity Per Population'] = merged_df['Total Capacity'] / merged_df['Population']
merged_df['Revenue Per Capita'] = merged_df['Total Revenue (AUD)'] / merged_df['Population']
merged_df['Frequency Weighted Venue Density'] = (merged_df['Venue Count'] * merged_df['Avg Frequency']) / merged_df['Population'] * 10000
merged_df['Gig Density Score'] = merged_df['Venues Per 10k Population'] * merged_df['Avg Frequency']

# Sort alphabetically for the dropdown
sorted_lgas = sorted(merged_df['LGA'].unique())

# Create an HTML file with the visualization
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Victorian LGA Gig Density vs Revenue Analysis</title>
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
        .metrics-selector {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Victorian LGA Gig Density vs Revenue Analysis</h1>
        <div class="controls">
            <label for="lga-select">Select LGA to Highlight:</label>
            <select id="lga-select">
                <option value="all">-- All LGAs --</option>
                {LGA_OPTIONS}
            </select>
            <button id="highlight-btn">Highlight Selected LGA</button>
            
            <div class="metrics-selector">
                <label for="x-metric">X-Axis:</label>
                <select id="x-metric">
                    <option value="venues_per_10k">Venues Per 10,000 Population</option>
                    <option value="frequency_weighted">Frequency-Weighted Venue Density</option>
                    <option value="gig_density_score">Gig Density Score</option>
                    <option value="capacity_per_pop">Venue Capacity Per Population</option>
                    <option value="venue_count">Total Venue Count</option>
                    <option value="avg_frequency">Average Gig Frequency</option>
                </select>
                
                <label for="y-metric" style="margin-left: 20px;">Y-Axis:</label>
                <select id="y-metric">
                    <option value="revenue_per_capita">Revenue Per Capita</option>
                    <option value="total_revenue">Total Revenue</option>
                </select>
                
                <button id="update-metrics-btn" style="margin-left: 10px;">Update Chart</button>
            </div>
            
            <div class="highlight-info">
                Select metrics to compare and highlight specific LGAs. Bubble size represents average venue capacity, and color represents average gig frequency.
            </div>
        </div>
        <div id="chart" style="width: 100%; height: 800px;"></div>
    </div>

    <script>
        // Data for the plot
        const lgas = {LGA_LIST};
        const venueCount = {VENUE_COUNT};
        const avgFrequency = {AVG_FREQUENCY};
        const totalCapacity = {TOTAL_CAPACITY};
        const avgCapacity = {AVG_CAPACITY};
        const population = {POPULATION};
        const totalRevenue = {TOTAL_REVENUE};
        const venuesPer10k = {VENUES_PER_10K};
        const revenuePerCapita = {REVENUE_PER_CAPITA};
        const capacityPerPop = {CAPACITY_PER_POP};
        const frequencyWeighted = {FREQUENCY_WEIGHTED};
        const gigDensityScore = {GIG_DENSITY_SCORE};
        
        // Create the data with custom hover text
        function createHoverText(i) {
            const formattedRevenue = totalRevenue[i].toLocaleString('en-AU', {
                style: 'currency',
                currency: 'AUD',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            });
            
            const formattedRevenuePerCapita = revenuePerCapita[i].toLocaleString('en-AU', {
                style: 'currency',
                currency: 'AUD',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            });
            
            return `<b>${lgas[i]}</b><br>` +
                   `Population: ${population[i].toLocaleString()}<br>` +
                   `Venues: ${venueCount[i]}<br>` +
                   `Venues Per 10k Pop: ${venuesPer10k[i].toFixed(2)}<br>` +
                   `Avg Frequency: ${avgFrequency[i].toFixed(2)} gigs/month<br>` +
                   `Avg Venue Capacity: ${avgCapacity[i].toFixed(0)}<br>` +
                   `Gig Density Score: ${gigDensityScore[i].toFixed(2)}<br>` +
                   `Total Revenue: ${formattedRevenue}<br>` +
                   `Revenue Per Capita: ${formattedRevenuePerCapita}`;
        }
        
        // Get X and Y values based on selected metrics
        function getMetricValues() {
            const xMetric = document.getElementById('x-metric').value;
            const yMetric = document.getElementById('y-metric').value;
            
            let xValues, yValues, xTitle, yTitle;
            
            // X-axis metric
            switch(xMetric) {
                case 'venues_per_10k':
                    xValues = venuesPer10k;
                    xTitle = 'Venues Per 10,000 Population';
                    break;
                case 'frequency_weighted':
                    xValues = frequencyWeighted;
                    xTitle = 'Frequency-Weighted Venue Density';
                    break;
                case 'gig_density_score':
                    xValues = gigDensityScore;
                    xTitle = 'Gig Density Score (Venues per 10k × Avg Frequency)';
                    break;
                case 'capacity_per_pop':
                    xValues = capacityPerPop;
                    xTitle = 'Venue Capacity Per Population';
                    break;
                case 'venue_count':
                    xValues = venueCount;
                    xTitle = 'Total Venue Count';
                    break;
                case 'avg_frequency':
                    xValues = avgFrequency;
                    xTitle = 'Average Gig Frequency (per month)';
                    break;
                default:
                    xValues = venuesPer10k;
                    xTitle = 'Venues Per 10,000 Population';
            }
            
            // Y-axis metric
            switch(yMetric) {
                case 'revenue_per_capita':
                    yValues = revenuePerCapita;
                    yTitle = 'Revenue Per Capita (AUD)';
                    break;
                case 'total_revenue':
                    yValues = totalRevenue;
                    yTitle = 'Total Revenue (AUD)';
                    break;
                default:
                    yValues = revenuePerCapita;
                    yTitle = 'Revenue Per Capita (AUD)';
            }
            
            return { xValues, yValues, xTitle, yTitle };
        }
        
        // Function to create the plot with all LGAs
        function createPlot() {
            const metrics = getMetricValues();
            const hoverTexts = [];
            
            for (let i = 0; i < lgas.length; i++) {
                hoverTexts.push(createHoverText(i));
            }
            
            // Calculate bubble sizes based on average capacity
            const maxCapacity = Math.max(...avgCapacity);
            const bubbleSizes = avgCapacity.map(cap => Math.max(Math.sqrt(cap / maxCapacity) * 30, 8));
            
            const trace = {
                x: metrics.xValues,
                y: metrics.yValues,
                mode: 'markers',
                type: 'scatter',
                text: hoverTexts,
                hoverinfo: 'text',
                marker: {
                    size: bubbleSizes,
                    color: avgFrequency,
                    colorscale: 'Viridis',
                    colorbar: {
                        title: 'Avg Gigs<br>Per Month'
                    },
                    line: {
                        width: 1,
                        color: 'darkgray'
                    }
                }
            };
            
            const layout = {
                title: 'Victorian LGA Gig Density vs Revenue Analysis<br>Bubble Size = Average Venue Capacity',
                xaxis: {
                    title: metrics.xTitle,
                    gridcolor: 'rgba(200, 200, 200, 0.5)'
                },
                yaxis: {
                    title: metrics.yTitle,
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
                }
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
            
            const metrics = getMetricValues();
            
            // Create hover texts
            const hoverTexts = [];
            for (let i = 0; i < lgas.length; i++) {
                hoverTexts.push(createHoverText(i));
            }
            
            // Calculate bubble sizes based on average capacity
            const maxCapacity = Math.max(...avgCapacity);
            const bubbleSizes = avgCapacity.map(cap => Math.max(Math.sqrt(cap / maxCapacity) * 30, 8));
            const highlightedSizes = [...bubbleSizes];
            highlightedSizes[lgaIndex] = Math.max(bubbleSizes[lgaIndex] * 1.5, 15); // Make highlighted bubble larger
            
            // Create a trace for all LGAs
            const trace = {
                x: metrics.xValues,
                y: metrics.yValues,
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
                title: `Victorian LGA Gig Density vs Revenue Analysis: ${selectedLGA} Highlighted<br>Bubble Size = Average Venue Capacity`,
                xaxis: {
                    title: metrics.xTitle,
                    gridcolor: 'rgba(200, 200, 200, 0.5)'
                },
                yaxis: {
                    title: metrics.yTitle,
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
                }
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
        
        // Update the chart when metrics change
        document.getElementById('update-metrics-btn').addEventListener('click', function() {
            const selectedLGA = document.getElementById('lga-select').value;
            if (selectedLGA === 'all') {
                createPlot();
            } else {
                highlightLGA(selectedLGA);
            }
        });
    </script>
</body>
</html>
"""

# Generate the dropdown options
lga_options = "\n                ".join([f'<option value="{lga}">{lga}</option>' for lga in sorted_lgas])

# Replace placeholders with actual data
html_content = html_content.replace("{LGA_OPTIONS}", lga_options)
html_content = html_content.replace("{LGA_LIST}", str(merged_df['LGA'].tolist()))
html_content = html_content.replace("{VENUE_COUNT}", str(merged_df['Venue Count'].tolist()))
html_content = html_content.replace("{AVG_FREQUENCY}", str(merged_df['Avg Frequency'].tolist()))
html_content = html_content.replace("{TOTAL_CAPACITY}", str(merged_df['Total Capacity'].tolist()))
html_content = html_content.replace("{AVG_CAPACITY}", str(merged_df['Avg Capacity'].tolist()))
html_content = html_content.replace("{POPULATION}", str(merged_df['Population'].tolist()))
html_content = html_content.replace("{TOTAL_REVENUE}", str(merged_df['Total Revenue (AUD)'].tolist()))
html_content = html_content.replace("{VENUES_PER_10K}", str(merged_df['Venues Per 10k Population'].tolist()))
html_content = html_content.replace("{REVENUE_PER_CAPITA}", str(merged_df['Revenue Per Capita'].tolist()))
html_content = html_content.replace("{CAPACITY_PER_POP}", str(merged_df['Total Capacity Per Population'].tolist()))
html_content = html_content.replace("{FREQUENCY_WEIGHTED}", str(merged_df['Frequency Weighted Venue Density'].tolist()))
html_content = html_content.replace("{GIG_DENSITY_SCORE}", str(merged_df['Gig Density Score'].tolist()))

# Write to file
with open('complete_lga_gig_density_revenue.html', 'w') as f:
    f.write(html_content)

# Create a CSV with the complete merged data for further analysis
merged_df.to_csv('complete_lga_gig_density_revenue_data.csv', index=False)

print("Created complete gig density vs revenue visualization: complete_lga_gig_density_revenue.html")
print("Also saved complete merged data to: complete_lga_gig_density_revenue_data.csv")
print("\nOpen the HTML file in a web browser to see the visualization with:")
print("1. Multiple gig density metrics options for the x-axis")
print("2. Revenue metrics options for the y-axis")
print("3. Bubble size scaled by average venue capacity")
print("4. Bubble color representing average gig frequency")
print("5. Interactive highlighting and metric selection")
print("6. Data from all Victorian LGAs with complete revenue and population data")

# Print some basic correlation analysis
print("\nCorrelation Analysis:")
print("Correlation between Venues Per 10k Population and Revenue Per Capita:", 
      np.corrcoef(merged_df['Venues Per 10k Population'], merged_df['Revenue Per Capita'])[0,1])
print("Correlation between Frequency Weighted Venue Density and Revenue Per Capita:", 
      np.corrcoef(merged_df['Frequency Weighted Venue Density'], merged_df['Revenue Per Capita'])[0,1])
print("Correlation between Gig Density Score and Revenue Per Capita:", 
      np.corrcoef(merged_df['Gig Density Score'], merged_df['Revenue Per Capita'])[0,1])