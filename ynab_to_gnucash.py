import csv
from datetime import datetime
from decimal import Decimal
import gnucash
from gnucash import Session, Transaction, Split, GncNumeric

def import_ynab_to_gnucash(input_file, gnucash_file):
    session = Session(gnucash_file)
    book = session.book
    root = book.get_root_account()
    
    with open(input_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            date = datetime.strptime(row['Date'], '%Y-%m-%d')
            payee = row['Payee']
            category = row['Category Group/Category']
            memo = row['Memo']
            outflow = Decimal(row['Outflow'] or '0')
            inflow = Decimal(row['Inflow'] or '0')
            amount = inflow - outflow  # Positive for inflow, negative for outflow
            
            from_account = find_account(root, row['Account'])
            to_account = find_account(root, category)
            
            trans = Transaction(book)
            trans.BeginEdit()
            trans.SetCurrency(from_account.GetCommodity())
            trans.SetDate(date.day, date.month, date.year)
            trans.SetDescription(payee)
            trans.SetNotes(memo)
            
            split1 = Split(book)
            split1.SetParent(trans)
            split1.SetAccount(from_account)
            split1.SetValue(GncNumeric(int(amount * 100), 100))
            split1.SetAmount(GncNumeric(int(amount * 100), 100))
            
            split2 = Split(book)
            split2.SetParent(trans)
            split2.SetAccount(to_account)
            split2.SetValue(GncNumeric(int(-amount * 100), 100))
            split2.SetAmount(GncNumeric(int(-amount * 100), 100))
            
            trans.CommitEdit()
    
    session.save()
    session.end()
    session.destroy()
    print("Import completed successfully.")

def find_account(root, name):
    acc = root.lookup_by_name(name)
    if acc is None:
        acc = gnucash.Account(root.get_book())
        acc.SetName(name)
        acc.SetType(gnucash.ACCT_TYPE_EXPENSE)
        acc.SetCommodity(root.get_commodity())
        root.append_child(acc)
    return acc

def main():
    input_file = 'path/to/your/ynab_export.csv'
    gnucash_file = 'path/to/your/gnucash_file.gnucash'
    import_ynab_to_gnucash(input_file, gnucash_file)

if __name__ == "__main__":
    main()