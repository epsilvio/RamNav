"""import mysql.connector

mydb = mysql.connector.connect(
    host="20.101.71.189",
    user="azureuser",
    password="ramnav",
    database="ramnav-db"
)

mycursor = mydb.cursor()

mycursor.execute("SELECT * FROM Rooms")

myresult = mycursor.fetchall()

for x in myresult:
    print(x)

mydb.close()"""

import pyodbc
cnxn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};User ID=ramnav;Password=password;Server=20.101.71.189;Database=ramnav-db;Port=3306')
cursor = cnxn.cursor()
cursor.execute("SELECT * FROM Rooms")
row = cursor.fetchone()
while row:
    print(row)
    row = cursor.fetchone()
cnxn.close()
