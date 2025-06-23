import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Function to add data labels to horizontal bars
def add_labels(ax, fontsize, is_float=False):
    for p in ax.patches:
        width = p.get_width()
        # Create the text label
        format_str = '{:1.1f}' if is_float else '{:1.0f}'
        label_text = format_str.format(width)
        # Position the text.
        if width > ax.get_xlim()[1] * 0.1: # Heuristic
             x_pos = width - (ax.get_xlim()[1] * 0.01)
             ha = 'right'
             color = 'white'
        else:
             x_pos = width + (ax.get_xlim()[1] * 0.01)
             ha = 'left'
             color = 'black'

        ax.text(x_pos, p.get_y() + p.get_height()/2.,
                label_text,
                ha=ha, va='center', color=color,
                fontweight='bold', fontsize=fontsize)


# Load the generated league tables
try:
    lga_league_table = pd.read_csv('lga_league_table.csv')
    tourism_league_table = pd.read_csv('tourism_league_table.csv')
except FileNotFoundError as e:
    print(f"Error loading CSV file: {e}")
    print("Please run create_league_tables.py first to generate the league tables.")
    exit()

# --- Font and Style Setup ---
# Set base font size and increase it
base_fontsize = plt.rcParams['font.size']
new_fontsize = base_fontsize * 1.07
y_label_fontsize = new_fontsize * 1.25
sns.set(style="whitegrid", font_scale=1.07)


# --- LGA Visualizations ---

# --- Data Trimming and Preparation ---
# Sort the DataFrame and keep all but the bottom 32
lga_revenue_data = lga_league_table.sort_values('Council Revenue', ascending=False).iloc[:-32]
lga_venues_data = lga_league_table.sort_values('number_of_venues', ascending=False).iloc[:-32]
lga_gigs_data = lga_league_table.sort_values('number_of_gigs', ascending=False).iloc[:-32]

# Convert revenue to millions for the plot
lga_revenue_data['Council Revenue (Millions)'] = lga_revenue_data['Council Revenue'] / 1_000_000


# 1. Council Revenue by LGA
plt.figure(figsize=(38.4, 20.5))
ax1 = sns.barplot(y='LGA', x='Council Revenue (Millions)', data=lga_revenue_data)
ax1.tick_params(axis='y', labelsize=y_label_fontsize)
ax1.set_xticks(np.arange(0, lga_revenue_data['Council Revenue (Millions)'].max() + 50, 50))
add_labels(ax1, fontsize=new_fontsize, is_float=True)
plt.title('Council Revenue by LGA (Excluding Bottom 32)', fontsize=new_fontsize*1.2)
plt.xlabel('Council Revenue (Millions of AUD)', fontsize=new_fontsize)
plt.ylabel('LGA', fontsize=new_fontsize)
plt.tight_layout()
plt.savefig('lga_council_revenue.png')
plt.close()

# 2. Number of Venues by LGA
plt.figure(figsize=(38.4, 20.5))
ax2 = sns.barplot(y='LGA', x='number_of_venues', data=lga_venues_data)
ax2.tick_params(axis='y', labelsize=y_label_fontsize)
ax2.set_xticks(np.arange(0, lga_venues_data['number_of_venues'].max() + 10, 10))
add_labels(ax2, fontsize=new_fontsize)
plt.title('Number of Venues by LGA (Excluding Bottom 32)', fontsize=new_fontsize*1.2)
plt.xlabel('Number of Venues', fontsize=new_fontsize)
plt.ylabel('LGA', fontsize=new_fontsize)
plt.tight_layout()
plt.savefig('lga_number_of_venues.png')
plt.close()

# 3. Number of Gigs by LGA
plt.figure(figsize=(38.4, 20.5))
ax3 = sns.barplot(y='LGA', x='number_of_gigs', data=lga_gigs_data)
ax3.tick_params(axis='y', labelsize=y_label_fontsize)
ax3.set_xticks(np.arange(0, lga_gigs_data['number_of_gigs'].max() + 10, 10))
add_labels(ax3, fontsize=new_fontsize, is_float=True)
plt.title('Estimated Number of Gigs per Week by LGA (Excluding Bottom 32)', fontsize=new_fontsize*1.2)
plt.xlabel('Estimated Number of Gigs per Week', fontsize=new_fontsize)
plt.ylabel('LGA', fontsize=new_fontsize)
plt.tight_layout()
plt.savefig('lga_number_of_gigs.png')
plt.close()


# --- Tourism Region Visualizations (Unchanged) ---

# 4. Number of Venues by Tourism Region
plt.figure(figsize=(10, 8))
ax4 = sns.barplot(y='Tourism Region', x='number_of_venues', data=tourism_league_table.sort_values('number_of_venues', ascending=False))
add_labels(ax4, fontsize=base_fontsize)
plt.title('Number of Venues by Tourism Region')
plt.xlabel('Number of Venues')
plt.ylabel('Tourism Region')
plt.tight_layout()
plt.savefig('tourism_region_number_of_venues.png')
plt.close()

# 5. Number of Gigs by Tourism Region
plt.figure(figsize=(10, 8))
ax5 = sns.barplot(y='Tourism Region', x='number_of_gigs', data=tourism_league_table.sort_values('number_of_gigs', ascending=False))
add_labels(ax5, fontsize=base_fontsize, is_float=True)
plt.title('Estimated Number of Gigs per Week by Tourism Region')
plt.xlabel('Estimated Number of Gigs per Week')
plt.ylabel('Tourism Region')
plt.tight_layout()
plt.savefig('tourism_region_number_of_gigs.png')
plt.close()

print("Visualizations have been generated and saved as PNG files.")