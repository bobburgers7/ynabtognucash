import csv
import sys
import os
from datetime import datetime
import gnucash
from gnucash import Session, Transaction, Split, GncNumeric, Account, GnuCashBackendException
from decimal import Decimal

def import_ynab_to_gnucash(input_file, gnucash_file):
    # Check if the GnuCash file exists
    file_exists = os.path.isfile(gnucash_file)

    try:
        # If the file doesn't exist, create it
        if not file_exists:
            session = Session()
            book = session.book
            root = book.get_root_account()
            USD = book.get_table().lookup('CURRENCY', 'USD')
            session.save(gnucash_file)
            session.end()
        
        # Now open the file (whether it existed before or we just created it)
        session = Session(gnucash_file)
        book = session.book
        root = book.get_root_account()
        USD = book.get_table().lookup('CURRENCY', 'USD')

        # Function to find or create an account
        def find_or_create_account(name, account_type):
            account = root.lookup_by_name(name)
            if account is None:
                account = Account(book)
                account.set_name(name)
                account.set_type(account_type)
                account.set_commodity(USD)
                root.append_child(account)
            return account

        # Read the YNAB CSV file
        with open(input_file, 'r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            
            for row in reader:
                try:
                    date = datetime.strptime(row['Date'], '%m/%d/%Y')
                    description = row['Payee']
                    account_name = row['Account']
                    memo = row['Memo']
                    category = row['Category Group/Category']
                    
                    outflow = Decimal(row['Outflow'].replace('$', '').replace(',', '') or '0')
                    inflow = Decimal(row['Inflow'].replace('$', '').replace(',', '') or '0')
                    amount = inflow - outflow

                    # Create the transaction
                    tx = Transaction(book)
                    tx.BeginEdit()
                    tx.SetCurrency(USD)
                    tx.SetDate(date.day, date.month, date.year)
                    tx.SetDescription(description)
                    tx.SetNotes(memo)

                    # Set up the splits
                    account = find_or_create_account(account_name, gnucash.ACCT_TYPE_BANK)
                    category_account = find_or_create_account(category, gnucash.ACCT_TYPE_EXPENSE)

                    # Main split (for the account)
                    split1 = Split(book)
                    split1.SetParent(tx)
                    split1.SetAccount(account)
                    split1.SetValue(GncNumeric(int(amount * 100), 100))  # GnuCash uses integer math
                    split1.SetAmount(GncNumeric(int(amount * 100), 100))

                    # Category split
                    split2 = Split(book)
                    split2.SetParent(tx)
                    split2.SetAccount(category_account)
                    split2.SetValue(GncNumeric(int(-amount * 100), 100))
                    split2.SetAmount(GncNumeric(int(-amount * 100), 100))

                    tx.CommitEdit()

                except KeyError as e:
                    print(f"Error: Missing column {e}. Row data: {row}")
                except ValueError as e:
                    print(f"Error parsing data: {e}. Row data: {row}")

        # Save and close the GnuCash file
        session.save()
        session.end()
        session.destroy()
        print(f"Import complete. GnuCash file updated: {gnucash_file}")

    except GnuCashBackendException as e:
        print(f"Error opening or creating GnuCash file: {e}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_ynab_file.csv> <gnucash_file.gnucash>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    gnucash_file = sys.argv[2]
    
    import_ynab_to_gnucash(input_file, gnucash_file)

if __name__ == "__main__":
    main()