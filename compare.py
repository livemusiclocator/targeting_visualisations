import pandas as pd
import numpy as np

def clean_venue_name(name):
    """Clean venue names for better matching"""
    if pd.isna(name):
        return name
    # Remove quotes and extra whitespace
    return name.replace("'", "").strip()

def format_value(val):
    """Format values for display, handling NaN and formatting numbers"""
    if pd.isna(val):
        return "N/A"
    # Convert float that are actually integers to integers (remove decimal)
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    return str(val)

# Load the CSV files
print("Loading CSV files...")
old = pd.read_csv("7oct.csv", low_memory=False)
new = pd.read_csv("22jun.csv", low_memory=False)

print(f"Old dataset columns: {len(old.columns)} columns")
print(f"New dataset columns: {len(new.columns)} columns")

# Clean up the venue names for better matching
old['Clean Venue Name'] = old['Venue Name'].apply(clean_venue_name)
new['Clean Venue Name'] = new['Venue Name'].apply(clean_venue_name)

# Use Venue Name as the key column
KEYS = ["Clean Venue Name"]
print(f"Using {KEYS} as key column(s) for comparison")

# Find common, added, and removed venues
print("\nAnalyzing differences between datasets...")
both = old.merge(new, on=KEYS, how="inner", suffixes=("_old", "_new"))
added = new.merge(old, on=KEYS, how="left", indicator=True)\
            .query("_merge == 'left_only'").drop(columns="_merge")
removed = old.merge(new, on=KEYS, how="left", indicator=True)\
             .query("_merge == 'left_only'").drop(columns="_merge")

# Generate a summary of the differences
print("\n===== SUMMARY OF DIFFERENCES =====")
print(f"Total venues in old dataset (7oct.csv): {len(old)}")
print(f"Total venues in new dataset (22jun.csv): {len(new)}")
print(f"Venues in both datasets: {len(both)}")
print(f"Venues added in new dataset: {len(added)}")
print(f"Venues removed from old dataset: {len(removed)}")

# Show examples of added and removed venues
if len(added) > 0:
    print("\n----- EXAMPLES OF ADDED VENUES (in new dataset only) -----")
    sample_size = min(10, len(added))
    sample_added = added.sample(sample_size) if len(added) > sample_size else added
    for idx, row in sample_added.iterrows():
        venue_name = row.get('Venue Name', row.get('Clean Venue Name', 'Unknown'))
        suburb = format_value(row.get('Suburb', 'Unknown'))
        state = format_value(row.get('State', ''))
        postcode = format_value(row.get('Postcode', ''))
        print(f"  • {venue_name} ({suburb}, {state} {postcode})")

if len(removed) > 0:
    print("\n----- EXAMPLES OF REMOVED VENUES (in old dataset only) -----")
    sample_size = min(10, len(removed))
    sample_removed = removed.sample(sample_size) if len(removed) > sample_size else removed
    for idx, row in sample_removed.iterrows():
        venue_name = row.get('Venue Name', row.get('Clean Venue Name', 'Unknown'))
        suburb = format_value(row.get('Suburb', 'Unknown'))
        state = format_value(row.get('State', ''))
        postcode = format_value(row.get('Postcode', ''))
        print(f"  • {venue_name} ({suburb}, {state} {postcode})")

# For venues in both datasets, analyze column changes
print("\n----- COLUMN DIFFERENCES FOR COMMON VENUES -----")
# Find columns that exist in both datasets (excluding the key column and suffixed columns)
common_cols = []
for col_old in old.columns:
    if col_old not in KEYS and col_old in new.columns:
        common_cols.append(col_old)

# For each common venue, check if values differ for each common column
change_stats = {}
total_changes = 0
# Make sure we only process venues that actually exist in both datasets
for venue_name in both['Clean Venue Name'].unique():
    # Find corresponding rows in original dataframes
    old_rows = old[old['Clean Venue Name'] == venue_name]
    new_rows = new[new['Clean Venue Name'] == venue_name]
    
    if len(old_rows) == 0 or len(new_rows) == 0:
        continue
        
    old_row = old_rows.iloc[0]
    new_row = new_rows.iloc[0]
    
    for col in common_cols:
        old_val = old_row[col]
        new_val = new_row[col]
        
        # Check if values are different (handling NaN values)
        if pd.isna(old_val) and pd.isna(new_val):
            continue
        elif pd.isna(old_val) and not pd.isna(new_val):
            changed = True
        elif not pd.isna(old_val) and pd.isna(new_val):
            changed = True
        else:
            changed = str(old_val) != str(new_val)
            
        if changed:
            total_changes += 1
            if col not in change_stats:
                change_stats[col] = 1
            else:
                change_stats[col] += 1

print(f"Total value changes across all common venues: {total_changes}")
print("\nColumns with the most changes:")
sorted_changes = sorted(change_stats.items(), key=lambda x: x[1], reverse=True)
for col, count in sorted_changes[:10]:  # Show top 10 changed columns
    percentage = (count / len(both)) * 100
    print(f"  • {col}: {count} changes ({percentage:.1f}% of common venues)")

# Show specific examples of changed values
if total_changes > 0:
    print("\n----- EXAMPLES OF SPECIFIC CHANGES -----")
    # Skip postcode changes as they're mostly formatting (.0 removed)
    interesting_changes = [col for col in sorted_changes if col[0] != 'Postcode']
    
    # Group examples by column type for better organization
    print("\n----- SIGNIFICANT COLUMN CHANGES (examples) -----")
    examples_by_column = {}
    
    # For each interesting column, find examples
    for col, count in interesting_changes[:8]:  # Use top 8 changed columns excluding Postcode
        examples_by_column[col] = []
        
        for venue_name in both['Clean Venue Name'].unique():
            if len(examples_by_column[col]) >= 3:  # Limit to 3 examples per column
                break
                
            # Find corresponding rows in original dataframes
            old_rows = old[old['Clean Venue Name'] == venue_name]
            new_rows = new[new['Clean Venue Name'] == venue_name]
            
            if len(old_rows) == 0 or len(new_rows) == 0:
                continue
                
            old_row = old_rows.iloc[0]
            new_row = new_rows.iloc[0]
            
            # Skip if column doesn't exist in either dataframe
            if col not in old_row or col not in new_row:
                continue
                
            old_val = old_row[col]
            new_val = new_row[col]
            
            # Check if values are different
            if pd.isna(old_val) and pd.isna(new_val):
                continue
            elif pd.isna(old_val) and not pd.isna(new_val):
                changed = True
                old_display = "N/A"
                new_display = format_value(new_val)
            elif not pd.isna(old_val) and pd.isna(new_val):
                changed = True
                old_display = format_value(old_val)
                new_display = "N/A"
            else:
                # Handle float formatting (remove .0)
                changed = format_value(old_val) != format_value(new_val)
                old_display = format_value(old_val)
                new_display = format_value(new_val)
                
            if changed:
                # Get venue name safely
                if 'Venue Name' in old_row and not pd.isna(old_row['Venue Name']):
                    venue_display = old_row['Venue Name']
                elif 'Venue Name' in new_row and not pd.isna(new_row['Venue Name']):
                    venue_display = new_row['Venue Name']
                else:
                    venue_display = venue_name  # Fall back to clean venue name
                    
                # Skip if the change looks like just a float formatting change
                if old_display.replace('.0', '') == new_display:
                    continue
                if new_display.replace('.0', '') == old_display:
                    continue
                    
                examples_by_column[col].append((venue_display, old_display, new_display))
    
    # Display examples organized by column
    for col, examples in examples_by_column.items():
        if examples:  # Only show columns that have examples
            print(f"\n  Column: '{col}' - {len(examples)} examples")
            for venue, old_val, new_val in examples:
                print(f"    • {venue}: changed from '{old_val}' to '{new_val}'")

    # Show new columns that were added
    new_cols = set(new.columns) - set(old.columns)
    if new_cols:
        print("\n----- NEW COLUMNS ADDED -----")
        for col in sorted(new_cols):
            print(f"  • {col}")
            
    # Show columns that were removed
    removed_cols = set(old.columns) - set(new.columns)
    if removed_cols:
        print("\n----- COLUMNS REMOVED -----")
        for col in sorted(removed_cols):
            print(f"  • {col}")

print("\n===== END OF COMPARISON =====")
