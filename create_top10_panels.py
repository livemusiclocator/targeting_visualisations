import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_table_panel(data, title, filename, column_labels=None, formatters=None):
    """
    Creates a PNG image panel from a pandas DataFrame.
    """
    if column_labels is None:
        column_labels = data.columns
    
    # Prepare data for the table
    cell_text = []
    for row in range(len(data)):
        row_data = data.iloc[row]
        formatted_row = []
        for i, col in enumerate(data.columns):
            if formatters and col in formatters:
                formatted_row.append(formatters[col](row_data[col]))
            else:
                formatted_row.append(row_data[col])
        cell_text.append(formatted_row)

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 4)) # Adjust size as needed
    ax.axis('tight')
    ax.axis('off')

    # Add table
    the_table = ax.table(cellText=cell_text, colLabels=column_labels, loc='center', cellLoc='left')
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(12)
    the_table.scale(1.2, 1.2)

    # Style table
    for (row, col), cell in the_table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#40466e')
        else:
            cell.set_facecolor(['#f0f0f0', '#ffffff'][row % 2])
        cell.set_edgecolor('w')
        cell.set_height(0.1)

    # Add title
    plt.title(title, fontsize=16, weight='bold', pad=20)
    
    # Save the figure
    plt.savefig(filename, bbox_inches='tight', dpi=150)
    plt.close()
    print(f"Panel saved to {filename}")

# --- Main Script ---
try:
    lga_league_table = pd.read_csv('lga_league_table.csv')
except FileNotFoundError as e:
    print(f"Error loading CSV file: {e}")
    print("Please run create_league_tables.py first.")
    exit()

# --- 1. Top 10 Council Revenue Panel ---
top_10_revenue = lga_league_table.sort_values('Council Revenue', ascending=False).head(10)
top_10_revenue['Council Revenue'] = (top_10_revenue['Council Revenue'] / 1_000_000).round(1) # Convert to millions
create_table_panel(
    data=top_10_revenue[['LGA', 'Council Revenue']],
    title='Top 10 LGAs by Council Revenue',
    filename='top10_lga_council_revenue.png',
    column_labels=['LGA', 'Revenue (Millions, AUD)'],
    formatters={'Council Revenue': lambda x: f'${x:,.1f}M'}
)

# --- 2. Top 10 Number of Venues Panel ---
top_10_venues = lga_league_table.sort_values('number_of_venues', ascending=False).head(10)
create_table_panel(
    data=top_10_venues[['LGA', 'number_of_venues']],
    title='Top 10 LGAs by Number of Venues',
    filename='top10_lga_number_of_venues.png',
    column_labels=['LGA', 'Number of Venues']
)

# --- 3. Top 10 Number of Gigs Panel ---
top_10_gigs = lga_league_table.sort_values('number_of_gigs', ascending=False).head(10)
top_10_gigs['number_of_gigs'] = top_10_gigs['number_of_gigs'].round(1)
create_table_panel(
    data=top_10_gigs[['LGA', 'number_of_gigs']],
    title='Top 10 LGAs by Number of Gigs',
    filename='top10_lga_number_of_gigs.png',
    column_labels=['LGA', 'Estimated Gigs per Week']
)