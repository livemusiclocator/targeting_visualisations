import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Load the revpop.csv file
print("Loading revpop.csv file...")
df = pd.read_csv("revpop.csv")

print(f"Dataset has {len(df)} rows and {len(df.columns)} columns")

# Calculate revenue per capita for sizing and coloring
df['Revenue Per Capita'] = df['Total Revenue (AUD)'] / df['Population']

# Format the LGA names to match with the previous dataset format if needed
df['LGA'] = df['LGA Name']

# Sort alphabetically for the dropdown
sorted_lgas = sorted(df['LGA'].unique())

# Create an HTML file with the final version combining all features
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>LGA Revenue vs Population Analysis</title>
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
        <h1>LGA Revenue vs Population Analysis</h1>
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
        const population = {POPULATION_LIST};
        const revenue = {REVENUE_LIST};
        const revenuePerCapita = {REVENUE_PER_CAPITA_LIST};
        const avgRevenuePerCapita = {AVG_REVENUE_PER_CAPITA};
        
        // Create the data with custom hover text
        function createHoverText(i) {
            const formattedRevenue = revenue[i].toLocaleString('en-AU', {
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
                   `Total Revenue: ${formattedRevenue}<br>` +
                   `Revenue Per Capita: ${formattedRevenuePerCapita}`;
        }
        
        // Calculate bubble sizes based on revenue per capita
        function calculateSizes(values, scaleFactor = 20, minSize = 10) {
            const maxValue = Math.max(...values);
            return values.map(value => Math.max(Math.sqrt(value / maxValue) * scaleFactor, minSize));
        }
        
        // Function to create the plot with all LGAs
        function createPlot() {
            const hoverTexts = [];
            for (let i = 0; i < lgas.length; i++) {
                hoverTexts.push(createHoverText(i));
            }
            
            // Calculate sizes based on revenue per capita
            const bubbleSizes = calculateSizes(revenuePerCapita);
            
            const trace = {
                x: population,
                y: revenue,
                mode: 'markers',
                type: 'scatter',
                text: hoverTexts,
                hoverinfo: 'text',
                marker: {
                    size: bubbleSizes,
                    color: revenuePerCapita,
                    colorscale: 'Viridis',
                    colorbar: {
                        title: 'Revenue<br>Per Capita<br>(AUD)'
                    },
                    line: {
                        width: 1,
                        color: 'darkgray'
                    }
                }
            };
            
            const layout = {
                title: 'Interactive Bubble Chart: LGA Population vs. Total Revenue<br>Bubble Size = Revenue Per Capita',
                xaxis: {
                    title: 'Population',
                    gridcolor: 'rgba(200, 200, 200, 0.5)',
                    type: 'log',  // Using log scale for better visualization with varying population sizes
                    tickformat: '.0f'  // No decimal places in tick labels
                },
                yaxis: {
                    title: 'Total Revenue (AUD)',
                    gridcolor: 'rgba(200, 200, 200, 0.5)',
                    type: 'log',  // Using log scale for better visualization with varying revenue values
                    tickformat: '.0f'  // No decimal places in tick labels
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
                    x0: Math.min(...population) * 0.9,
                    y0: avgRevenuePerCapita * Math.min(...population) * 0.9,
                    x1: Math.max(...population) * 1.1,
                    y1: avgRevenuePerCapita * Math.max(...population) * 1.1,
                    line: {
                        color: 'red',
                        width: 1,
                        dash: 'dash'
                    }
                }],
                annotations: [{
                    x: Math.max(...population) * 0.9,
                    y: avgRevenuePerCapita * Math.max(...population) * 0.9,
                    text: `Average Revenue Per Capita: $${Math.round(avgRevenuePerCapita).toLocaleString()}`,
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
            for (let i = 0; i < lgas.length; i++) {
                hoverTexts.push(createHoverText(i));
            }
            
            // Calculate sizes based on revenue per capita, but make highlighted one larger
            const regularSizes = calculateSizes(revenuePerCapita);
            const highlightedSizes = [...regularSizes];
            highlightedSizes[lgaIndex] = Math.max(regularSizes[lgaIndex] * 1.5, 15); // Make highlighted bubble larger
            
            // Create a trace for all LGAs
            const trace = {
                x: population,
                y: revenue,
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
                title: `Interactive Bubble Chart: ${selectedLGA} Highlighted<br>LGA Population vs. Total Revenue`,
                xaxis: {
                    title: 'Population',
                    gridcolor: 'rgba(200, 200, 200, 0.5)',
                    type: 'log',  // Using log scale for better visualization with varying population sizes
                    tickformat: '.0f'  // No decimal places in tick labels
                },
                yaxis: {
                    title: 'Total Revenue (AUD)',
                    gridcolor: 'rgba(200, 200, 200, 0.5)',
                    type: 'log',  // Using log scale for better visualization with varying revenue values
                    tickformat: '.0f'  // No decimal places in tick labels
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
                    x0: Math.min(...population) * 0.9,
                    y0: avgRevenuePerCapita * Math.min(...population) * 0.9,
                    x1: Math.max(...population) * 1.1,
                    y1: avgRevenuePerCapita * Math.max(...population) * 1.1,
                    line: {
                        color: 'red',
                        width: 1,
                        dash: 'dash'
                    }
                }],
                annotations: [{
                    x: Math.max(...population) * 0.9,
                    y: avgRevenuePerCapita * Math.max(...population) * 0.9,
                    text: `Average Revenue Per Capita: $${Math.round(avgRevenuePerCapita).toLocaleString()}`,
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

# Calculate average revenue per capita
avg_revenue_per_capita = df['Revenue Per Capita'].mean()

# Replace placeholders with actual data
html_content = html_content.replace("{LGA_OPTIONS}", lga_options)
html_content = html_content.replace("{LGA_LIST}", str(df['LGA'].tolist()))
html_content = html_content.replace("{POPULATION_LIST}", str(df['Population'].tolist()))
html_content = html_content.replace("{REVENUE_LIST}", str(df['Total Revenue (AUD)'].tolist()))
html_content = html_content.replace("{REVENUE_PER_CAPITA_LIST}", str(df['Revenue Per Capita'].tolist()))
html_content = html_content.replace("{AVG_REVENUE_PER_CAPITA}", str(avg_revenue_per_capita))

# Write to file
with open('lga_revenue_population.html', 'w') as f:
    f.write(html_content)

print("Created revenue vs population visualization: lga_revenue_population.html")
print("\nOpen the HTML file in a web browser to see the visualization with:")
print("1. LGA population on x-axis (log scale)")
print("2. Total revenue on y-axis (log scale)")
print("3. Bubble size scaled by revenue per capita")
print("4. A diagonal reference line showing average revenue per capita")
print("5. Interactive highlighting of LGAs")