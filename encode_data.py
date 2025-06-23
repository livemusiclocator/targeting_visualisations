import base64
import os

# --- Configuration ---
# List of CSV files to encode
files_to_encode = [
    'lga_league_table.csv',
    'tourism_league_table.csv',
    'lga_interactive_chart_data.csv'
]

# Output JavaScript file
output_js_file = 'encoded_data.js'

# --- Main Script ---
def encode_csv_files():
    """
    Reads specified CSV files, encodes them to Base64, and saves them
    into a single JavaScript file as a dictionary.
    """
    encoded_data = {}

    for filename in files_to_encode:
        try:
            with open(filename, 'rb') as f:
                # Read the raw binary content of the file
                raw_content = f.read()
                # Encode the content to Base64
                encoded_content = base64.b64encode(raw_content)
                # Store it as a UTF-8 string for the JS file
                encoded_data[filename] = encoded_content.decode('utf-8')
            print(f"Successfully read and encoded '{filename}'.")
        except FileNotFoundError:
            print(f"Warning: File not found and will be skipped: '{filename}'")
            continue
    
    # --- Write to JavaScript file ---
    # Create the JavaScript content
    js_content = "const encodedData = {\n"
    for filename, content in encoded_data.items():
        js_content += f'    "{filename}": "{content}",\n'
    js_content += "};"

    try:
        with open(output_js_file, 'w') as f:
            f.write(js_content)
        print(f"\nSuccessfully created '{output_js_file}' with encoded data.")
    except IOError as e:
        print(f"\nError writing to JavaScript file: {e}")

if __name__ == '__main__':
    encode_csv_files()