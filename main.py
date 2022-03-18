import speech_recognition as sr
import json
import pyodbc
from PIL import Image
import requests
from io import BytesIO
from time import sleep
import os
import time


file = open('wordbank.json')
wordbank = json.load(file)
AZURE_SPEECH_KEY = "d2216ffb09af4c27ad2df097eb7f3cd3"
AZURELOCATION = "southeastasia"
rooms = []
cls = lambda: os.system('cls' if os.name == 'nt' else 'clear')

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print("""
    Importing the Speech SDK for Python failed.
    Refer to
    https://docs.microsoft.com/azure/cognitive-services/speech-service/quickstart-python for
    installation instructions.
    """)
    import sys

    sys.exit(1)


def get_query():
    print("Hi, what room/facility are you looking for?")
    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)

    # write audio to a WAV file
    with open("query.wav", "wb") as f:
        f.write(audio.get_wav_data())

    # obtain path to "results.wav" in the same folder as this script
    from os import path

    AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "query.wav")

    # use the audio file as the audio source
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)  # read the entire audio file

    query = r.recognize_azure(audio, key=AZURE_SPEECH_KEY, location=AZURELOCATION)

    # remove if last character is not a letter
    while query and not query[-1].isalpha():
        query = query[:-1]

    try:
        print("I think you said: " + query)
        process_query(query)
    except sr.UnknownValueError:
        print("I did not understand what you said, please try again.")
        wait_keyword()
    except sr.RequestError as e:
        print("Could not request results from the server; {0}".format(e))
        wait_keyword()


def process_query(query):
    # split the text
    words = query.split()

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
        print("Sorry no keywords found in your query, please try again.")
        wait_keyword()
    else:
        if counter > 1:
            show_choices(rooms)
        else:
            show_result(rooms)


def show_choices(choices):
    num = 0
    print("Your query returned multiple possible results:")
    for choice in choices:
        for ele in wordbank:
            tmp = wordbank[ele][0]
            if tmp["room_id"] == choice:
                num += 1
                print(str(num) + ". " + ele)

    try:
        index = int(input("Which one do you choose? (Say the name): "))
        show_result(choices[index - 1])
    except ValueError as e:
        print("Please enter a valid answer")


def show_result(id):
    server = 'ramnav.database.windows.net'
    database = 'ramnav'
    username = 'ramnav_admin'
    password = 'Nextgen2021'
    driver = '{ODBC Driver 18 for SQL Server}'

    with pyodbc.connect(
            'DRIVER=' + driver + ';SERVER=tcp:' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM dbo.rooms WHERE room_id = " + id[0])
            row = cursor.fetchone()
            while row:
                print("Room Name: " + str(row[1]) + "\nRoom Number: " + str(row[2]) + "\nFloor Level: " + str(
                    row[3]) + "\nImage Link: " + str(row[4]))
                try:
                    response = requests.get(str(row[4]))
                    img = Image.open(BytesIO(response.content))
                    sleep(1)
                    img.show()
                except ValueError:
                    print("No available image for this location!")
                row = cursor.fetchone()
                rooms.clear()
                time.sleep(2)
                wait_keyword()


def wait_keyword():
    """runs keyword spotting locally, with direct access to the result audio"""
    # Creates an instance of a keyword recognition model. Update this to
    # point to the location of your keyword recognition model.
    model = speechsdk.KeywordRecognitionModel("RamNav-Trigger.table")

    # The phrase your keyword recognition model triggers on.
    keyword = "Hey RamNav"

    # Create a local keyword recognizer with the default microphone device for input.
    keyword_recognizer = speechsdk.KeywordRecognizer()

    done = False

    def recognized_cb(evt):
        # Only a keyword phrase is recognized. The result cannot be 'NoMatch'
        # and there is no timeout. The recognizer runs until a keyword phrase
        # is detected or recognition is canceled (by stop_recognition_async()
        # or due to the end of an input file or stream).
        result = evt.result
        if result.reason == speechsdk.ResultReason.RecognizedKeyword:
            # print("Hi, what room/facility are you looking for?")
            time.sleep(0.5)

        nonlocal done
        done = True

    def canceled_cb(evt):
        result = evt.result
        if result.reason == speechsdk.ResultReason.Canceled:
            print('Keyword Waiting Canceled')
        nonlocal done
        done = True

    # Connect callbacks to the events fired by the keyword recognizer.
    keyword_recognizer.recognized.connect(recognized_cb)
    keyword_recognizer.canceled.connect(canceled_cb)

    # Start keyword recognition.
    # clear()
    result_future = keyword_recognizer.recognize_once_async(model)
    print('Say "Hey, RamNav!" to start searching...')
    result = result_future.get()

    # Read result audio (incl. the keyword).
    if result.reason == speechsdk.ResultReason.RecognizedKeyword:
        time.sleep(2)  # give some time so the stream is filled
        result_stream = speechsdk.AudioDataStream(result)
        result_stream.detach_input()  # stop any more data from input getting to the stream
        get_query()

        # save_future = result_stream.save_to_wav_file_async("AudioFromRecognizedKeyword.wav")
        # print('Saving file...')
        # saved = save_future.get()

    # If active keyword recognition needs to be stopped before results, it can be done with
    #
    #   stop_future = keyword_recognizer.stop_recognition_async()
    #   print('Stopping...')
    #   stopped = stop_future.get()


#wait_keyword()
