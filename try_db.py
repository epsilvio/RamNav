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

import requests

file = requests.get('http://ramnav.westeurope.cloudapp.azure.com/js/dictionary.json')
wordbank = file.json()
txt = ("Where can I play basketball")
counter = 0
rooms = []

for key1 in wordbank.keys():
    for key2 in wordbank[key1][0].keys():
        if wordbank[key1][0][key2].lower() in txt.lower():
            counter += 1
            room_id = key1
            rooms.append(room_id)
            break
print(wordbank)
#print(wordbank['215'][0]['keyword1'].lower() in txt.lower())