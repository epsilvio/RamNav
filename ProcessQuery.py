import threading
import json
import pyodbc

file = open('wordbank.json')
wordbank = json.load(file)
rooms = []


class ProcessQuery(threading.Thread):
    def __init__(self, query):
        super(ProcessQuery, self).__init__()
        self.query = query
        self.msg = None
        self.result = None

    def run(self):
        # Clear rooms variable
        rooms.clear()
        # split the text
        words = self.query.split()

        # check for keywords
        counter = 0
        for i in words:
            for j in wordbank:
                if i.lower() == j:
                    counter += 1
                    # Print the success message and the value of the key
                    room_id = wordbank[j][0]
                    # print(i.lower() + "'s room id is " + room_id["room_id"])
                    rooms.append(room_id["room_id"])

        if counter == 0:
            # Print the message if the value does not exist
            self.msg = "Sorry no keywords found in your query, please try again."
        else:
            self.msg = "Your query returned " + str(counter) + " possible results."

        self.result = rooms


class ShowChoices(threading.Thread):
    def __init__(self, choices):
        super(ShowChoices, self).__init__()
        self.choices = choices
        self.msg = None

    def run(self):
        num = 0
        tmp_msg = "Your query returned multiple possible results:\nWhich one do you choose? (Say the name):\n"
        for choice in self.choices:
            for ele in wordbank:
                tmp = wordbank[ele][0]
                if tmp["room_id"] == choice:
                    num += 1
                    tmp_msg += str(num) + ". " + ele + "\n"
        self.msg = tmp_msg


class ShowResult(threading.Thread):
    def __init__(self, id):
        super(ShowResult, self).__init__()
        self.id = id
        self.server = 'ramnav.database.windows.net'
        self.database = 'ramnav'
        self.username = 'ramnav_admin'
        self.password = 'Nextgen2021'
        self.driver = '{ODBC Driver 18 for SQL Server}'
        self.result = None

    def run(self):
        with pyodbc.connect(
                'DRIVER=' + self.driver + ';SERVER=tcp:' + self.server + ';PORT=1433;DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.rooms WHERE room_id = " + self.id[0])
                row = cursor.fetchone()
                while row:
                    self.result = {
                        "Name": str(row[1]),
                        "Number": str(row[2]),
                        "Level": str(row[3]),
                    }
                    row = cursor.fetchone()
                    rooms.clear()
