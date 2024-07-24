import re
import argparse

def convert_bofa_to_chase(bofa_qfx, chase_qfx):
    print(f'Processing Bank of America QFX file: {bofa_qfx}')
    print(f'Writing Chase-style QFX file to: {chase_qfx}')

    try:
        # Read the Bank of America QFX file
        with open(bofa_qfx, 'r', encoding='utf-8') as f:
            bofa_data = f.read()

        # Extract header, transactions, and footer from BofA QFX
        header_end = bofa_data.find('<BANKTRANLIST>')
        footer_start = bofa_data.rfind('</BANKTRANLIST>') + len('</BANKTRANLIST>')

        if header_end == -1 or footer_start == -1:
            raise ValueError("Unable to find <BANKTRANLIST> tags in the input file.")

        header = bofa_data[:header_end].strip()
        footer = bofa_data[footer_start:].strip()
        transactions = bofa_data[header_end + len('<BANKTRANLIST>'):footer_start - len('</BANKTRANLIST>')].strip()

        # Process STMTTRN entries
        stmttrn_pattern = re.compile(r'<STMTTRN>.*?</STMTTRN>', re.DOTALL)
        remove_tags_pattern = re.compile(r'<(DTUSER|MERCHCAT|EXPCAT|CARDNUM|CARDNAME|MCC)>\s*.*?\n', re.DOTALL)

        def process_stmttrn(match):
            stmttrn_data = match.group(0)
            # Remove specific tags
            stmttrn_data = re.sub(remove_tags_pattern, '', stmttrn_data)
            # Remove extraneous whitespace
            stmttrn_data = stmttrn_data.strip()
            stmttrn_data = '\n'.join(line.lstrip() for line in stmttrn_data.split('\n'))
            return f'{stmttrn_data}\n'

        # Apply transformations to the transactions
        stmttrns = stmttrn_pattern.finditer(transactions)
        processed_stmttrns = [process_stmttrn(m) for m in stmttrns]

        # Write the Chase-style QFX file
        with open(chase_qfx, 'w', encoding='utf-8') as f:
            f.write(header)
            f.write('<BANKTRANLIST>\n')  # Add opening BANKTRANLIST tag
            f.writelines(processed_stmttrns)
            f.write('</BANKTRANLIST>\n')  # Add closing BANKTRANLIST tag
            f.write(footer)
            print(f'Chase-style QFX file "{chase_qfx}" created.')

    except Exception as e:
        print(f"An error occurred: {e}")

# Main function to parse arguments and execute
def main():
    parser = argparse.ArgumentParser(description='Convert Bank of America QFX to Chase-style QFX.')
    parser.add_argument('bofa_qfx', type=str, help='Path to the Bank of America QFX file')
    parser.add_argument('chase_qfx', type=str, help='Path to the output Chase-style QFX file')

    args = parser.parse_args()
    convert_bofa_to_chase(args.bofa_qfx, args.chase_qfx)

if __name__ == '__main__':
    main()