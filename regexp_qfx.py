import re
import csv
import argparse


def process_qfx_and_update_csv(qfx_input, qfx_output, dictionary_csv, unmatched_dictionary_csv):
    print(f'Processing QFX file: {qfx_input}')
    print(f'Writing updated QFX data to: {qfx_output}')
    print(f'Using dictionary CSV file: {dictionary_csv}')
    print(f'Writing unmatched names to: {unmatched_dictionary_csv}')

    # Regular expression to extract and replace the NAME field in QFX entries
    name_pattern = re.compile(r'<NAME>(.*?)\n', re.DOTALL)

    # Dictionary to store normalized entries and their variations
    normalized_entries = {}
    variation_to_normalized = {}
    unmatched_entries = set()  # Use a set to avoid duplicates

    # Define regular expressions for known patterns
    known_patterns = {
        r'amazon\.com\*.*': 'Amazon',
        r'amzn mktp us\*.*': 'Amazon',
        r'barnes &amp; noble #\d+': 'Barnes & Noble',
        r'target\.com  \*.*': 'Target',
        r'target\s+\d+.*': 'Target',
        # Add more patterns as needed
    }

    # Read existing dictionary CSV file
    try:
        with open(dictionary_csv, 'r', newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            header = next(csv_reader)  # Read header row
            print(f'Reading CSV file: {dictionary_csv}')

            for row in csv_reader:
                if row:  # Skip empty rows
                    normalized_name = row[0]
                    variations = [v.strip() for v in row[1:] if v.strip()]
                    if normalized_name and variations:  # Ensure no empty entries
                        normalized_entries[normalized_name] = variations

                        # Map variations to the normalized name
                        for variation in variations:
                            variation_to_normalized[variation.lower()] = normalized_name

                        print(f'Added existing entry: {normalized_name} -> Variations: {variations}')
    except FileNotFoundError:
        print(f"CSV file '{dictionary_csv}' not found. No data to process.")

    # Read the QFX file and process
    with open(qfx_input, 'r', encoding='utf-8') as f:
        qfx_data = f.read()
        print(f'Reading QFX file: {qfx_input}')

        def replace_name(match):
            original_name = match.group(1).strip()
            normalized_name = normalize_name(original_name)
            normalized_name_lower = normalized_name.lower()

            if normalized_name_lower in variation_to_normalized:
                replacement = variation_to_normalized[normalized_name_lower]
                print(f'Found match: "{original_name}" -> Replacing with "{replacement}"')
                return f'<NAME>{replacement}\n'
            else:
                # Use regex patterns to find a match
                for pattern, base_name in known_patterns.items():
                    if re.match(pattern, original_name, re.IGNORECASE):
                        print(f'Pattern match: "{original_name}" -> Replacing with "{base_name}"')
                        return f'<NAME>{base_name}\n'

                # Add unmatched name and suggested normalized name to the set
                suggested_normalized_name = normalize_name(original_name)
                unmatched_entries.add((suggested_normalized_name, original_name))
                # If no match found, use original name
                print(f'No match found for "{original_name}". Using original name.')
                return f'<NAME>{original_name}\n'

        # Find all STMTTRN elements in QFX data
        stmttrn_pattern = re.compile(r'<STMTTRN>.*?</STMTTRN>', re.DOTALL)
        stmttrn_matches = stmttrn_pattern.finditer(qfx_data)

        for stmttrn_match in stmttrn_matches:
            stmttrn_data = stmttrn_match.group(0)
            name_matches = name_pattern.finditer(stmttrn_data)

            for name_match in name_matches:
                original_name = name_match.group(1).strip()
                replacement = replace_name(name_match)
                print(f'Original Name: "{original_name}" -> Replacement: "{replacement}"')

                # Replace NAME field within the specific STMTTRN element
                updated_stmttrn_data = name_pattern.sub(replacement, stmttrn_data)
                qfx_data = qfx_data.replace(stmttrn_data, updated_stmttrn_data)

        # Write updated QFX data to the new file
        with open(qfx_output, 'w', encoding='utf-8') as f:
            f.write(qfx_data)
            print(f'QFX file "{qfx_output}" created.')

    # Sort dictionary entries alphabetically by normalized name
    sorted_entries = sorted(normalized_entries.items())
    with open(dictionary_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Normalized Name', 'Variations'])
        for normalized_name, variations in sorted_entries:
            if variations:  # Ensure no empty rows are written
                row = [normalized_name] + variations
                writer.writerow(row)
        print(f'Dictionary CSV file "{dictionary_csv}" updated and sorted.')

    # Write unmatched names with suggested normalized names to the CSV output file
    with open(unmatched_dictionary_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Suggested Normalized Name', 'Original Name'])
        for normalized_name, original_name in sorted(unmatched_entries):
            writer.writerow([normalized_name, original_name])
        print(f'Unmatched names written to "{unmatched_dictionary_csv}".')


def normalize_name(name):
    # Convert name to title case with exceptions for articles, conjunctions, and prepositions
    exceptions = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'by', 'with', 'of'}
    words = name.split()
    normalized_name = ' '.join(
        word.capitalize() if (word.lower() not in exceptions or i == 0) else word.lower() for i, word in
        enumerate(words))
    print(f'Normalized "{name}" -> "{normalized_name}"')
    return normalized_name


# Main function to parse arguments and execute
def main():
    parser = argparse.ArgumentParser(description='Process QFX file and update CSV with normalized NAME entries.')
    parser.add_argument('qfx_input', type=str, help='Path to the QFX input file')
    parser.add_argument('qfx_output', type=str, help='Path to the QFX output file')
    parser.add_argument('dictionary_csv', type=str, help='Path to the dictionary CSV file')
    parser.add_argument('unmatched_dictionary_csv', type=str, help='Path to the unmatched names CSV file')

    args = parser.parse_args()
    process_qfx_and_update_csv(args.qfx_input, args.qfx_output, args.dictionary_csv, args.unmatched_dictionary_csv)


if __name__ == '__main__':
    main()
