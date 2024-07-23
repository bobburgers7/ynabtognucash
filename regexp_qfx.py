import re
import csv
import argparse

def process_qfx_and_update_csv(qfx_file, csv_file):
    print(f'Processing QFX file: {qfx_file}')
    print(f'Using CSV file: {csv_file}')

    # Regular expression to extract and replace the NAME field in QFX entries
    name_pattern = re.compile(r'<NAME>(.*?)</NAME>', re.DOTALL)

    # Dictionary to store normalized entries and their matches
    normalized_entries = {}

    # Read existing CSV file to update or create
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            header = next(csv_reader)  # Read header row
            print(f'Reading CSV file: {csv_file}')

            for row in csv_reader:
                normalized_name = row[0]
                matches = row[1:]
                normalized_entries[normalized_name] = matches
                print(f'Added normalized entry: {normalized_name} -> Matches: {matches}')
    except FileNotFoundError:
        print(f"CSV file '{csv_file}' not found. Creating new CSV file.")

    # Read the QFX file and process
    with open(qfx_file, 'r', encoding='utf-8') as f:
        qfx_data = f.read()
        print(f'Reading QFX file: {qfx_file}')

        def replace_name(match):
            original_name = match.group(1)
            if original_name in normalized_entries:
                replacement = normalized_entries[original_name][0]
                print(f'Found match: "{original_name}" -> Replacing with "{replacement}"')
                return f'<NAME>{replacement}</NAME>'
            else:
                # Check for entries similar to original_name and replace with original_name
                for norm_name, matches in normalized_entries.items():
                    for match in matches:
                        if original_name.lower() in match.lower():
                            normalized_entries[original_name] = normalized_entries[norm_name]
                            replacement = normalized_entries[original_name][0]
                            print(f'Found similar match: "{original_name}" in "{match}" -> Replacing with "{replacement}"')
                            return f'<NAME>{replacement}</NAME>'
                # If no similar entry found, normalize the name
                normalized_name = normalize_name(original_name)
                normalized_entries[original_name] = [normalized_name]
                print(f'No match found for "{original_name}". Normalized to "{normalized_name}"')
                return f'<NAME>{normalized_name}</NAME>'

        # Find all STMTTRN elements in QFX data
        stmttrn_pattern = re.compile(r'<STMTTRN>.*?</STMTTRN>', re.DOTALL)
        stmttrn_matches = stmttrn_pattern.finditer(qfx_data)

        for stmttrn_match in stmttrn_matches:
            stmttrn_data = stmttrn_match.group(0)
            name_matches = name_pattern.finditer(stmttrn_data)

            for name_match in name_matches:
                original_name = name_match.group(1)
                replacement = replace_name(name_match)
                print(f'Original Name: "{original_name}" -> Replacement: "{replacement}"')

                # Replace NAME field within the specific STMTTRN element
                updated_stmttrn_data = name_pattern.sub(replacement, stmttrn_data)
                qfx_data = qfx_data.replace(stmttrn_data, updated_stmttrn_data)

        # Write updated QFX data back to the original file
        with open(qfx_file, 'w', encoding='utf-8') as f:
            f.write(qfx_data)
            print(f'QFX file "{qfx_file}" updated.')

    # Write normalized entries and matches to the CSV file with multiple columns
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Normalized Name'] + header[1:])  # Write header row

        for normalized_name, matches in normalized_entries.items():
            row_to_write = [normalized_name] + matches
            csv_writer.writerow(row_to_write)
            print(f'Writing to CSV: {row_to_write}')

    print(f'CSV file "{csv_file}" maintained with multiple columns.')

def normalize_name(name):
    # Custom normalization function (you can modify this based on your specific needs)
    # Example: Convert to lowercase and remove extra spaces
    normalized_name = re.sub(r'\s+', ' ', name.strip().lower())
    print(f'Normalized "{name}" -> "{normalized_name}"')
    return normalized_name

# Main function to parse arguments and execute
def main():
    parser = argparse.ArgumentParser(description='Process QFX file and update CSV with normalized NAME entries.')
    parser.add_argument('qfx_file', type=str, help='Path to the QFX file')
    parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    args = parser.parse_args()
    process_qfx_and_update_csv(args.qfx_file, args.csv_file)

if __name__ == '__main__':
    main()
