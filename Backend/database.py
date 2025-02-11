import csv
import sqlite3

con = sqlite3.connect('database.db')
cursor = con.cursor()

# Create a table with the desired columns
query = "CREATE TABLE IF NOT EXISTS sys_command (  id INTEGER PRIMARY KEY,  name VARCHAR(100), path VARCHAR(1000))"
cursor.execute(query)

# Insert data into the table
# query = "INSERT INTO sys_command (null, '', '')"
# cursor.execute(query)
# con.commit()

query = "CREATE TABLE IF NOT EXISTS web_command (  id INTEGER PRIMARY KEY,  name VARCHAR(100), url VARCHAR(1000))"
cursor.execute(query)

# Insert data into the table
# query = "INSERT INTO web_command (null, '', '')"
# cursor.execute(query)
# con.commit()

# # Create a table with the desired columns
cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY, name VARCHAR(200), mobile_no VARCHAR(255))''')

# Specify the column indices you want to import (0-based index)
# Example: Importing the 1st and 3rd columns
desired_columns_indices = [0, 30]

# Read data from CSV and insert into SQLite table for the desired columns
with open('contacts.csv', 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        selected_data = [row[i] for i in desired_columns_indices]
        cursor.execute(''' INSERT INTO contacts (id, 'name', 'mobile_no') VALUES (null, ?, ?);''', tuple(selected_data))

# Commit changes and close connection
con.commit()
con.close()