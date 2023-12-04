import csv  # used for parsing the csv files we are importing
from datetime import datetime  # used to convert dates
from mysql.connector import connect # needed to connect to database

_RIDE_CSV = 'extract_data1.csv'
_BOOK_CSV = 'extract_data2.csv'
_DB = 'wpmb'
_USER = 'micah'
_PASSWORD = "password"


# Connect to the database
cnx = connect(user=_USER, password=_PASSWORD)
cursor = cnx.cursor()


# Create procedure to insert into Item table
CREATE_BOOK = """CALL TABLE ListBook (%s, %s, %s, %s, %s, %s);"""

CREATE_RIDE = """CALL TABLE ListRide (%s, %s, %s, %s, %s, %s, %s);"""


# Open the file, read each record iteratively, and insert to database
with open(_RIDE_CSV, 'r', encoding='utf-8') as csvFile:
    csvData = csv.DictReader(csvFile)
    for record in csvData:
        record['name'] = record['name'].strip()
        record['startingPrice'] = record['startingPrice'].strip()
        record['nltDate'] = record['nltDate'].strip()
        record['time'] = record['time'].strip()
        record['departureFrom'] = record['departureFrom'].strip()
        record['seatsAvailable'] = record['seatsAvailable'].strip()
        record['puserID'] = record['puserID'].strip()
        
        cursor.execute(CREATE_RIDE, record)

with open(_BOOK_CSV, 'r', encoding='utf-8') as csvFile:
    csvData = csv.DictReader(csvFile)
    for record in csvData:
        record['name'] = record['name'].strip()
        record['startingPrice'] = record['startingPrice'].strip()
        record['nltDate'] = record['nltDate'].strip()
        record['author'] = record['author'].strip()
        record['class'] = record['class'].strip()
        record['puserID'] = record['puserID'].strip()

        cursor.execute(CREATE_BOOK, record)


# Commit the transaction
cnx.commit()

# Close the connection to the database
cnx.close()
