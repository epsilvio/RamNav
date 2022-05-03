import threading
import time

import mysql.connector
import requests
import speech_recognition as sr

file = requests.get('http://ramnav.westeurope.cloudapp.azure.com/js/dictionary.json')
wordbank = file.json()
rooms = []
listener = sr.Recognizer()


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
        # words = self.query.split()

        # check for keywords
        counter = 0
        for key1 in wordbank.keys():
            for key2 in wordbank[key1][0].keys():
                if wordbank[key1][0][key2].lower() in self.query.lower():
                    counter += 1
                    room_id = key1
                    rooms.append(room_id)
                    break

        if counter == 0:
            # Print the message if the value does not exist
            self.msg = "Sorry no keywords found in your query, please try to rephrase."
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
        tmp_msg = "Which room are you referring to? (Say 'First', 'Second', or 'Third'):\n"
        for choice in self.choices:
            for key in wordbank.keys():
                tmp = key
                if tmp == choice:
                    num += 1
                    tmp_msg += str(num) + ". " + str(wordbank[key][0]['name']) + "\n"
        self.msg = tmp_msg


class GetChoice(threading.Thread):
    def __init__(self, recognizer, key, location, ids):
        super(GetChoice, self).__init__()
        self.recognizer = recognizer
        self.key = key
        self.location = location
        self.response = None
        self.uv = False
        self.re = False
        self.choice = None
        self.ids = ids
        self.ie = False

    def run(self):
        with sr.Microphone() as source:
            audio = self.recognizer.listen(source)

        # write audio to a WAV file
        with open("query2.wav", "wb") as f:
            f.write(audio.get_wav_data())

        # obtain path to "results.wav" in the same folder as this script
        from os import path

        AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "query2.wav")

        # use the audio file as the audio source
        with sr.AudioFile(AUDIO_FILE) as source:
            audio = self.recognizer.record(source)  # read the entire audio file

        query = self.recognizer.recognize_azure(audio, key=self.key, location=self.location)

        first = 0
        second = 0
        third = 0

        # Interpret query
        if 'first' in query.lower():
            first = 1
        if 'second' in query.lower():
            second = 1
        if 'third' in query.lower():
            third = 1
        try:
            if first+second+third != 1:
                self.response = "Invalid response, please try to query again.\n\nSay 'Hey, RamNav' to start searching."
                self.choice = None
            else:
                try:
                    if first == 1:
                        self.response = "You chose the first option! Please wait for the result..."
                        self.choice = []
                        self.choice.append(self.ids[0])
                        time.sleep(3)
                    if second == 1:
                        self.response = "You chose the second option! Please wait for the result..."
                        self.choice = []
                        self.choice.append(self.ids[1])
                        time.sleep(3)
                    if third == 1:
                        self.choice = []
                        self.response = "You chose the third option! Please wait for the result..."
                        self.choice.append(self.ids[2])
                        time.sleep(3)
                except IndexError:
                    self.response = None
                    self.ie = True
        except sr.UnknownValueError:
            self.response = None
            self.uv = True
        except sr.RequestError as e:
            self.response = None
            self.re = True


class ShowResult(threading.Thread):
    def __init__(self, id):
        super(ShowResult, self).__init__()
        self.id = id
        self.host = "20.101.71.189",
        self.user = "azureuser",
        self.password = "ramnav",
        self.database = "ramnav-db"
        self.result = None

    def run(self):
        mydb = mysql.connector.connect(
            host="20.101.71.189",
            user="azureuser",
            password="ramnav",
            database="ramnav-db"
        )

        mycursor = mydb.cursor()
        mycursor.execute(
            "SELECT * FROM Rooms INNER JOIN Images ON Rooms.roomID = Images.imgID WHERE Rooms.roomID = " + self.id[0])
        myresult = mycursor.fetchone()

        while myresult:
            self.result = {
                "Name": str(myresult[1]),
                "Number": str(myresult[2]),
                "Level": str(myresult[3]),
                "Map-Link": str(myresult[5]),
                "QR-Link": str(myresult[6])
            }
            myresult = mycursor.fetchone()
            rooms.clear()

        mydb.close()
