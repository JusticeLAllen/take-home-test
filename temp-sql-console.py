import tkinter as tk 
from tkinter import ttk
import json
import sqlite3

# Steps:
# 1. Import given jsons, insert into tables
#   ^ This will take some finagling because sqlite does not play nice with json columns
#   ^ It also doesn't play nice with array columns, more on that later
# 2. Take data from "raw" tables and clean before inserting into final versions of tables
# 3. Open a text input window thru tkinter
#       (this will act as a console for interacting with our new db)
# 4. "Run" function which spits any query results into a new Text window
#       (Perhaps include the query that was run as a Nice To Have)

print("Starting a local sqlite session")
con = sqlite3.connect(":memory:")

print("Loading json files...")
receipt_json = []
with open(r'f:\receipts.json') as f:
    # This iterator gets around the fact that it's a newline delimited json blob
    for line in f:
        x = json.loads(line)
        receipt_json.append(x)
print("Receipts json loaded (1/3)")

users_json = []
with open(r'f:\users.json') as f:
    for line in f:
        x = json.loads(line)
        users_json.append(x)
print("Users json loaded (2/3)")

brands_json = []
with open(r'f:\brands.json') as f:
    for line in f:
        x = json.loads(line)
        brands_json.append(x)
print("Brands json loaded (3/3)")

print("Json files loaded. Creating empty tables...")
cur = con.cursor()

# First we'll create each table, before cleaning the jsons and inserting data
#   (Realistically if this data were coming into Snowflake or some such I would be using DBT)

# These columns are all based on the data model
cur.execute('''CREATE TABLE receipts_raw(receiptId, userId, barcode, brandCode,
dateScanned, purchasedItemCount, rewardsReceiptStatus, totalSpent, finalPrice, 
itemPrice, userFlaggedPrice)''')
print('Receipts tables created (1/3)')

cur.execute('''CREATE TABLE users_raw(userId, active, createdDate, state)''')
print('Users tables created (2/3)')

cur.execute('''CREATE TABLE brands_raw(brandId, barcode, brandCode, name, topBrand)''')
print('Brands table created (3/3)')

print('All tables are created, inserting raw data now.')
# This step will take the data from the jsons and sort out any issues presented by columns with arrays
#       (Essentially, I'll be using Python for what would be a lateral_flatten in a more robust SQL)
# The next step will then take the data from those tables and make sure the data types are appropriate

# RECEIPTS 
columns = ['receiptId', 'userId', 'barcode', 'brandCode', 'dateScanned', 'purchasedItemCount', 'rewardsReceiptStatus', 
'totalSpent', 'finalPrice', 'itemPrice', 'userFlaggedPrice']
# Each column will be matched to a value from the line in the json. That way we can circle back and 
#   fill in the blanks with NULLs later. 
cells = []
for i in columns:
    cells.append('')


for bit in receipt_json:
    key_list = list(bit.keys())
    value_list = list(bit.values())

    # This will be used in cases where one column has multiple sublists (really just rewardsReceiptItemList)
    sublistFound = False

    for key in key_list:
        # The not in list has the values of columns which are known to have arrays
        if key in columns and key not in ('dateScanned','rewardsReceiptItemList'):

            # I.e. "Find the index of the key that matched. 
            # Use that index to change the corresponding value in the cells list."
            # ^ These will be inserted into the table in just a bit and we need to know which are NULL
            cells[columns.index(key)] = "'" + str(value_list[key_list.index(key)]) + "'"

        # This one is broken out separately because I know the key won't match the column name
        if key == '_id':
            sub_keys = list(value_list[key_list.index(key)].keys())
            sub_values = list(value_list[key_list.index(key)].values())

            # Named in this case because I'm changing the column name to be more explicit (my preference)
            cells[columns.index('receiptId')] = sub_values[0]
            
        if key == 'rewardsReceiptItemList':
            # In some cases there will only be one Item on the list. In that case, no need to iterate further down
            if len(value_list[key_list.index(key)]) > 1:
                sublistFound = True
            
            else:
                sub_keys = list(value_list[key_list.index(key)][0].keys())
                sub_values = list(value_list[key_list.index(key)][0].values())

                for sub in sub_keys:
                    if sub in ('barcode', 'brandCode', 'itemPrice', 'finalPrice', 'userFlaggedPrice'):
                        cells[columns.index(sub)] = sub_values[sub_keys.index(sub)]

        if key == 'dateScanned':
            sub_keys = list(value_list[key_list.index(key)].keys())
            sub_values = list(value_list[key_list.index(key)].values())

            cells[columns.index(key)] = sub_values[0]
            
    # If there are no sublists in rewardsReceiptItemList, we can get away with doing this next step once
    if sublistFound is False:

        # Filling in any NULLs
        for cell in cells:
            if cell == '':
                cells[cells.index(cell)] = 'NULL'

        cur.execute('insert into receipts_raw values(?,?,?,?,?,?,?,?,?,?,?)', cells)
        

    else:
        # Filling in any NULLs (this is repeated here in case a sublist is missing a different column)
        x = 0
        for sublist in value_list[key_list.index('rewardsReceiptItemList')]:
            sub_keys = list(value_list[key_list.index('rewardsReceiptItemList')][x].keys())
            sub_values = list(value_list[key_list.index('rewardsReceiptItemList')][x].values())
            x += 1

            for sub in sub_keys:
                if sub in ('barcode', 'itemPrice', 'brandCode', 'finalPrice', 'userFlaggedPrice'):
                    cells[columns.index(sub)] = sub_values[sub_keys.index(sub)]

            for cell in cells:
                if cell == '':
                    cells[cells.index(cell)] = 'NULL'

            cur.execute('insert into receipts_raw values(?,?,?,?,?,?,?,?,?,?,?)', cells)

            # Wiping these columns bc some sublists might have certain columns while others won't
            # Don't want a value getting carried over from sublist to another
            for subitem in ('barcode', 'itemPrice', 'brandCode', 'finalPrice', 'userFlaggedPrice'):
                cells[columns.index(subitem)] = ''


    cells = []
    for i in columns:
        cells.append('')

# USERS
# This will go much the same way as receipts_raw but simpler
columns = ['userId', 'active', 'createdDate', 'state']
cells = []
for i in columns:
    cells.append('')

for bit in users_json:
    key_list = list(bit.keys())
    value_list = list(bit.values())

    for key in key_list:
        if key == '_id':
            sub_keys = list(value_list[key_list.index(key)].keys())
            sub_values = list(value_list[key_list.index(key)].values())

            cells[columns.index('userId')] = sub_values[0]

        if key == 'createdDate':
            sub_keys = list(value_list[key_list.index(key)].keys())
            sub_values = list(value_list[key_list.index(key)].values())

            cells[columns.index(key)] = sub_values[0]

        if key in columns and key not in ('_id', 'createdDate'):
            cells[columns.index(key)] = "'" + str(value_list[key_list.index(key)]) + "'"
        
    # Filling in any NULLs
    for cell in cells:
        if cell == '':
            cells[cells.index(cell)] = 'NULL'

    cur.execute('insert into users_raw values(?,?,?,?)', cells)
    cells = []
    for i in columns:
        cells.append('')

# BRANDS
columns = ['brandId', 'barcode', 'brandCode', 'name', 'topBrand']
cells = []
for i in columns:
    cells.append('')

for bit in brands_json:
    key_list = list(bit.keys())
    value_list = list(bit.values())

    for key in key_list:
        if key == '_id':
            sub_keys = list(value_list[key_list.index(key)].keys())
            sub_values = list(value_list[key_list.index(key)].values())

            cells[columns.index('brandId')] = sub_values[0]

        if key in columns:
            cells[columns.index(key)] = "'" + str(value_list[key_list.index(key)]) + "'"
        
    # Filling in any NULLs
    for cell in cells:
        if cell == '':
            cells[cells.index(cell)] = 'NULL'

    cur.execute('insert into brands_raw values(?,?,?,?,?)', cells)
    cells = []
    for i in columns:
        cells.append('')

print("Creating final tables now...")
# This will be casting the existing columns into the types needed, just in case
# It'll also convert the date columns from 13 digit unixepoch to 10 digit unixepoch 
#   (sqlite can't read 13 digit)
# Also also the boolean columns will remain varchar, another quirk
cur.execute('''CREATE TABLE receipt_items AS SELECT CAST(receiptId AS varchar) AS receiptId,
CAST(userId AS varchar) AS userId, QUOTE(CAST(barcode AS varchar)) AS barcode, 
QUOTE(CAST(brandCode AS varchar)) AS brandCode, date(SUBSTR(dateScanned, 1, 10), 'unixepoch') AS dateScanned,
CAST(purchasedItemCount AS int) AS purchasedItemCount, CAST(rewardsReceiptStatus AS varchar) AS rewardsReceiptStatus,
CAST(totalSpent AS float) AS totalSpent, CAST(finalPrice AS float) AS finalPrice,
CAST(itemPrice AS float) AS itemPrice, CAST(userFlaggedPrice AS float) AS userFlaggedPrice 
    FROM receipts_raw''')
cur.execute('''CREATE TABLE users AS SELECT CAST(userId AS varchar) AS userId, CAST(active AS varchar) AS active,
date(SUBSTR(createdDate, 1, 10), 'unixepoch') AS createdDate, CAST(state AS varchar) AS state 
    FROM users_raw''')
cur.execute('''CREATE TABLE brands AS SELECT CAST(brandId AS varchar) AS brandId, CAST(barcode AS varchar(100)) AS barcode,
CAST(brandCode AS varchar) AS brandCode, CAST(name AS varchar) AS name, CAST(topBrand AS varchar) AS topBrand
    FROM brands_raw''')

print("Final tables created!")

# This variable will hold our queries from the SQL console
# This is global for simplicity - no need to get into any variable passing here
global data_input

# Now that the tables are populated and the data is clean, we can prepare our SQL console
# This function will run queries typed into the root window
def run_query():

    print("Running query now.")
    inputted_query = data_input.get("1.0", 'end-1c')
    print("User query was:\n" + inputted_query)

    results_raw = cur.execute(inputted_query)

        
    # This bit adds column names before the results
    header_query = cur.execute(inputted_query)
    header_step2 = header_query.description
    headers = ''
    for head in header_step2:
        # Separate column names with a tab
        headers = headers + head[0] + '\t'

    # Quick and dirty way to get these to look somewhat normal in a text window
    # I don't anticipate using many results with a bunch of rows here but who knows
    results_modified = headers
    for row in results_raw.fetchall():
        results_modified = results_modified + '\n' + str(row)

    print("Results are in:\n" + str(results_modified))

    branch = tk.Tk()
    branch.title("Analyzed babyyyy")
    result_display = tk.Text(branch, wrap='word')
    result_display.grid(row=0, column=0)
    result_display.insert(tk.END, results_modified)

# tkinter formatting is a little funny -- all of the code above was nested 
#   inside of the only function this window will have (run_query)
# These lines are what generate the window and fill it with bits
root = tk.Tk()
root.title("Analyzin' Time")
root.geometry('400x400')
data_input = tk.Text(root, height=22, width=50, wrap='word')
# In other words, when they click the run_query() function will go off
cruncher = tk.Button(root, text='Run', command=run_query)

# Placeholder value to signify it's a Text field
data_input.insert(tk.END, 'SQL goes here')

data_input.grid(row=0, column=0, columnspan=2)
cruncher.grid(row=1, column=1)

# This is what keeps the main window open
root.mainloop()

