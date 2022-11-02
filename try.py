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

mydb.close()

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

'''
  For more samples please visit https://github.com/Azure-Samples/cognitive-services-speech-sdk 
'''

import azure.cognitiveservices.speech as speechsdk

# Creates an instance of a speech config with specified subscription key and service region.
speech_key = "f048a4008e8344a3a92f289da20f2738"
service_region = "southeastasia"

speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
# Note: the voice setting will not overwrite the voice element in input SSML.
speech_config.speech_synthesis_voice_name = "en-AU-WilliamNeural"

with open('script.txt', 'r') as file:
    data = file.read().replace('\n', '')

text = "Hello, I am RamNav!"

# use the default speaker as audio output.
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

result = speech_synthesizer.speak_text_async(data).get()
# Check result
if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesized for text [{}]".format(text))
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result.cancellation_details
    print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        print("Error details: {}".format(cancellation_details.error_details))

import qrcode
from PIL import Image

# Link for website
input_data = "http://ramnav.westeurope.cloudapp.azure.com"
#Creating an instance of qrcode
qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5)
qr.add_data(input_data)
qr.make(fit=True)
img = qr.make_image(fill='black', back_color='white')
img.save('qrcode.png')
# creating a object
im = Image.open('qrcode.png')
im.show()

import mysql.connector

room = ["201"]

mydb = mysql.connector.connect(
    host="ramnav-db.mysql.database.azure.com",
    user="azureuser",
    password="Nextgen2021",
    database="ramnav-db"
)
mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM Rooms INNER JOIN Images ON `roomID` = `imgID` WHERE `roomID` = " + room[0])
myresult = mycursor.fetchone()
print(myresult)
while myresult:
    result = {
        "Name": str(myresult[1]),
        "Number": str(myresult[2]),
        "Level": str(myresult[3])
        # "Map-Link": str(myresult[5]),
        # "QR-Link": str(myresult[6])
    }

mydb.close()

import ProcessQuery as PQ
import tkinter

root = tkinter.Tk()
param = ["205"]


def get_result(room):
    gr_thread = PQ.ShowResult(room)
    gr_thread.start()
    show_result(gr_thread)


def show_result(thread):
    if thread.is_alive():
        root.after(100, lambda: show_result(thread))
    else:
        print("here1")
        thread.join()
        if thread.result is not None:
            room = thread.result
            print(room[0])

        else:
            print("No Results")


get_result(param)

import time
try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print(
        "Importing the Speech SDK for Python failed. Refer to https://docs.microsoft.com/azure/cognitive-services/speech-service/quickstart-python for installation instructions.")
    import sys

    sys.exit(1)

sdk = speechsdk.KeywordRecognizer()
model = speechsdk.KeywordRecognitionModel("RamNav-Trigger.table")
keyword = "Hey RamNav"
response = None

def wait_key():
    done = False
    print("Listening...")
    def recognized_cb(evt):
        # Only a keyword phrase is recognized. The result cannot be 'NoMatch'
        # and there is no timeout. The recognizer runs until a keyword phrase
        # is detected or recognition is canceled (by stop_recognition_async()
        # or due to the end of an input file or stream).
        result = evt.result
        if result.reason == speechsdk.ResultReason.RecognizedKeyword:
            time.sleep(0.5)

        nonlocal done
        done = True
        print("Recognized!!")

    def canceled_cb(evt):
        result = evt.result
        if result.reason == speechsdk.ResultReason.Canceled:
            response = False
        nonlocal done
        done = True
        print("Cancelled!")

    # Connect callbacks to the events fired by the keyword recognizer.
    sdk.recognized.connect(recognized_cb)
    sdk.canceled.connect(canceled_cb)

    # Start keyword recognition.
    result_future = sdk.recognize_once_async(model)
    result = result_future.get()

    # Read result audio (incl. the keyword).
    if result.reason == speechsdk.ResultReason.RecognizedKeyword:
        time.sleep(2)  # give some time so the stream is filled
        result_stream = speechsdk.AudioDataStream(result)
        result_stream.detach_input()  # stop any more data from input getting to the stream
        response = True
        print("Recognized!")

import mysql.connector
mydb = mysql.connector.connect(
    host="ramnav-db.mysql.database.azure.com",
    user="azureuser",
    password="Nextgen2021",
    database="ramnav-db"
)
mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM Rooms INNER JOIN Images ON `roomID` = `imgID` WHERE `roomID` = 201")
myresult = mycursor.fetchone()
print(myresult[3])

import requests
import app
file = requests.get('http://ramnav.westeurope.cloudapp.azure.com/js/rooms.json')
wordbank = file.json()
rooms = []
query = "Where can i order food"
counter = 0
num = 0
tmp_msg = "Which room are you referring to? (Say 'First', 'Second', or 'Third'):\n"

for room in wordbank:
    for attr in room.keys():
        if attr != 'roomID':
            if room[attr].lower() in query.lower():
                counter += 1
                room_id = room
                rooms.append(room_id)
                break

for room in rooms:
    num += 1
    tmp_msg += str(num) + ". " + str(room['name']) + "\n"

if counter == 0:
    # Print the message if the value does not exist
    print("Sorry no keywords found in your query, please try to rephrase.")
else:
    #print("Your query returned " + str(counter) + " possible results.")
    print(tmp_msg)
import requests
import string
file = requests.get('http://ramnav.westeurope.cloudapp.azure.com/js/dictionary.json')
wordbank = file.json()
query = "Where is the room 1202"
counter = 0

#Remove unwanted punctuation mark in the end
if query and query[-1] in string.punctuation:
    query = query[:-1]

for room in wordbank:
    for attr in room.keys():
        if attr != 'roomID' and attr != 'roomNum':
            if room[attr].lower() in query.lower():
                counter += 1
                #room_id = room
                #rooms.append(room_id)
                break
        elif attr == 'roomNum':
            for word in query.lower().split():
                if word == room[attr].lower():
                    counter += 1
                    room_id = room
                    #rooms.append(room_id)
                    break
print(counter)
import re

sentence = 'Multi-purpose Hall 1'
word1 = 'Multipurpose'
word2 = 'Multipurpose Hall 1'
query = "Where is the Registrar's Office"
ban = ["Room", "Office", "Where is the"]
query = re.sub(r'[^A-Za-z0-9 ]+', '', query)
data = [{
    'id': 1, 'name1': 'a', 'name2': 'A', 'name3': 'Aa'
},{
    'id': 2, 'name1': 'b', 'name2': 'B', 'name3': ['Bb','BB']
},{
    'id': 3, 'name1': 'c', 'name2': 'C', 'name3': 'Cc'
}]

for ele in data:
    for attr in ele.keys():
        if 'name' in attr:
            print(attr + ' is a name attribute')
        else:
            print(attr + ' is not a name attribute')
print('BB' in data[1]['name3'])


import speech_recognition as sr
import requests
import re
file = requests.get('http://ramnav.westeurope.cloudapp.azure.com/js/dictionary.json')
wordbank = file.json()

print("Which room or facility are you looking for?")

#Get sound input from mic
with sr.Microphone() as source:
    audio = sr.Recognizer().listen(source)

#Write sound to WAV file
with open("query.wav", "wb") as f:
    f.write(audio.get_wav_data())

# obtain path to "query.wav" in the same folder as this script
from os import path
AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "query.wav")

# use the audio file as the audio source
with sr.AudioFile(AUDIO_FILE) as source:
    audio = sr.Recognizer().record(source)  # read the entire audio file

query = sr.Recognizer().recognize_azure(audio, key='d2216ffb09af4c27ad2df097eb7f3cd3', location='southeastasia')

print('I think you said: ', query)

rooms = []
rooms.clear()

# check for keywords
counter = 0
for room in wordbank:
    for attr in room.keys():
        if attr == 'name':
            name = re.sub(r'[^A-Za-z0-9 ]+', '', room['name'])
            for word in query.lower().split():
                for key in name.lower().split():
                    if word == key:
                        if room in rooms:
                            break
                        else:
                            counter += 1
                            room_id = room
                            rooms.append(room_id)
                            break
        elif 'keyword' in attr:
            if room[attr].lower() in query.lower():
                if room in rooms:
                    break
                else:
                    counter += 1
                    room_id = room
                    rooms.append(room_id)
                    break
        elif attr != 'roomID':
            for word in query.lower().split():
                if word == room[attr].lower():
                    if room in rooms:
                        break
                    else:
                        counter += 1
                        room_id = room
                        rooms.append(room_id)
                        break

if counter == 0:
    # Print the message if the value does not exist
    msg = "Sorry no keywords found in your query, please try to rephrase."
else:
    msg = "Your query returned " + str(counter) + " possible results."

result = rooms
print(result)"""

import os
import azure.cognitiveservices.speech as speechsdk

# Creates an instance of a speech config with specified subscription key and service region.
speech_key = "d2216ffb09af4c27ad2df097eb7f3cd3"
service_region = "southeastasia"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
# Note: the voice setting will not overwrite the voice element in input SSML.
speech_config.speech_synthesis_voice_name = 'en-US-JennyNeural'


speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

# Get text from the console and synthesize to the default speaker.
print("Enter some text that you want to speak >")
text = input()

speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesized for text [{}]".format(text))
elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = speech_synthesis_result.cancellation_details
    print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        if cancellation_details.error_details:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")




