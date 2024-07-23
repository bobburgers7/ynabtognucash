# ynabtognucash
YNAB to GnuCash Migration Tool

YNAB offers a CSV export of fall your data.  This is an attempt to import that easily into GNUCash 5.8 using the python-bindings module.


It assumes the YNAB file has these columns:

"Account","Flag","Date","Payee","Category Group/Category","Category Group","Category","Memo","Outflow","Inflow","Cleared"
