from mysql.connector import connect

# Connect to database
cnx = connect(user="micah",
              password="password",
              database="wpmb")

    # Get cursor
cursor = cnx.cursor(prepared=True)
query = "SELECT * FROM Users WHERE userID = %s"
cursor.execute(query, ('johndoe',))
result = cursor.fetchall()
print(result)
cnx.close()
