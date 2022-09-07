import threading
import time
import json
import requests
import speech_recognition as sr
import qrcode
import string
import re

file = requests.get('http://ramnav.westeurope.cloudapp.azure.com/js/dictionary.json')
wordbank = file.json()
rooms = []
listener = sr.Recognizer()
settings = json.load(open('assets/settings.json'))

class ProcessQuery(threading.Thread):
    def __init__(self, query):
        super(ProcessQuery, self).__init__()
        self.setDaemon(True)
        self.query = query
        self.msg = None
        self.result = None
        self.ban = ["Room", "Office", "A", "B", "C"]

    def run(self):
        # Clear rooms variable
        rooms.clear()

        #Remove unwanted punctuation mark in the end and non-alphanumeric characters
        if self.query and self.query[-1] in string.punctuation:
            self.query = self.query[:-1]
        self.query = re.sub(r'[^A-Za-z0-9 ]+', '', self.query)

        #Remove common words
        for word in self.ban:
            for key in self.query.split():
                if word.lower() == key.lower():
                    self.query = self.query.lower().replace(key.lower(), '')

        #Remove 'Where is the' problematic phrase
        if 'Where is the'.lower() in self.query.lower():
            self.query = self.query.lower().replace('where is the', '')

        #Print the preprocessed query
        print(self.query)

        # check for keywords
        counter = 0
        done = False
        for room in wordbank:
            for attr in room.keys():
                if attr == 'name':
                    name = re.sub(r'[^A-Za-z0-9 ]+', '', room['name'])
                    for word in self.query.lower().split():
                        for key in name.lower().split():
                            if word == key:
                                if room in rooms:
                                    break
                                else:
                                    counter += 1
                                    room_id = room
                                    rooms.append(room_id)
                                    done = True
                                    break
                elif attr != 'roomID':
                    for word in self.query.lower().split():
                        if word == room[attr].lower():
                            if room in rooms:
                                break
                            else:
                                counter += 1
                                room_id = room
                                rooms.append(room_id)
                                done = True
                                break

        if counter == 0:
            # Print the message if the value does not exist
            self.msg = "Sorry no keywords found in your query, please try to rephrase."
        else:
            self.msg = "Your query returned " + str(counter) + " possible results."

        self.result = rooms
        print(self.result)


class ShowChoices(threading.Thread):
    def __init__(self, choices):
        super(ShowChoices, self).__init__()
        self.setDaemon(True)
        self.choices = choices
        self.msg = None

    def run(self):
        num = 0
        tmp_msg = "Which room are you referring to? (Say 'First', 'Second', or 'Third'):\n"
        for room in rooms:
            num += 1
            tmp_msg += str(num) + ". " + str(room['name']) + "\n"
        self.msg = tmp_msg
        """for choice in self.choices:
            for key in wordbank.keys():
                tmp = key
                if tmp == choice:
                    num += 1
                    tmp_msg += str(num) + ". " + str(wordbank[key][0]['name']) + "\n"
        self.msg = tmp_msg"""


class GetChoice(threading.Thread):
    def __init__(self, recognizer, key, location, ids):
        super(GetChoice, self).__init__()
        self.setDaemon(True)
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
            self.recognizer.energy_threshold = settings[0]['mic_threshold']
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

        try:
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

            if first + second + third != 1:
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
        self.setDaemon(True)
        self.id = id
        self.result = None

    def run(self):
        """mydb = mysql.connector.connect(
            host="ramnav-db.mysql.database.azure.com",
            user="azureuser",
            password="Nextgen2021",
            database="ramnav-db"
        )
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM Rooms INNER JOIN Images ON `roomID` = `imgID` WHERE `roomID` = " + self.id[0])
        myresult = mycursor.fetchone()
        mydb.close()"""
        self.result = [self.id['roomID'], self.id['name'], self.id['roomNum'],
                       self.id['roomLvl'],
                       "http://ramnav.westeurope.cloudapp.azure.com/images/map/" + self.id['roomID'] + ".png"]
        self.create_qr(str(self.result[0]) + ".png")
        rooms.clear()

    @staticmethod
    def create_qr(room):
        # Link for website
        input_data = "http://ramnav.westeurope.cloudapp.azure.com/images/map/" + room
        # Creating an instance of qrcode
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5)
        qr.add_data(input_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img.save('qrcode.png')
