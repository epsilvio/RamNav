import tkinter
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import PIL
import json
import pyodbc
import requests
from io import BytesIO
from time import sleep
import os
import time
import threading
import speech_recognition as sr

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    messagebox.showwarning("""
                            Importing the Speech SDK for Python failed.
                            Refer to
                            https://docs.microsoft.com/azure/cognitive-services/speech-service/quickstart-python for
                            installation instructions.
                           """)
    import sys

    sys.exit(1)

# Global Variables
AZURE_SPEECH_KEY = "d2216ffb09af4c27ad2df097eb7f3cd3"
AZURELOCATION = "southeastasia"
file = open('wordbank.json')
wordbank = json.load(file)
rooms = []
listener = sr.Recognizer()


class AsyncRecog(threading.Thread):
    def __init__(self, recognizer, model, keyword):
        super(AsyncRecog, self).__init__()
        self.sdk = recognizer
        self.speech = model
        self.key = keyword
        self.response = None

    def run(self):
        done = False

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

        def canceled_cb(evt):
            result = evt.result
            if result.reason == speechsdk.ResultReason.Canceled:
                self.response = False
            nonlocal done
            done = True

        # Connect callbacks to the events fired by the keyword recognizer.
        self.sdk.recognized.connect(recognized_cb)
        self.sdk.canceled.connect(canceled_cb)

        # Start keyword recognition.
        result_future = self.sdk.recognize_once_async(self.speech)
        result = result_future.get()

        # Read result audio (incl. the keyword).
        if result.reason == speechsdk.ResultReason.RecognizedKeyword:
            time.sleep(2)  # give some time so the stream is filled
            result_stream = speechsdk.AudioDataStream(result)
            result_stream.detach_input()  # stop any more data from input getting to the stream
            self.response = True


class SearchRm(threading.Thread):
    def __init__(self, recognizer, key, location):
        super(SearchRm, self).__init__()
        self.recognizer = recognizer
        self.key = key
        self.location = location
        self.query = None

    def run(self):
        with sr.Microphone() as source:
            audio = self.recognizer.listen(source)

        # write audio to a WAV file
        with open("query.wav", "wb") as f:
            f.write(audio.get_wav_data())

        # obtain path to "results.wav" in the same folder as this script
        from os import path

        AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "query.wav")

        # use the audio file as the audio source
        with sr.AudioFile(AUDIO_FILE) as source:
            audio = self.recognizer.record(source)  # read the entire audio file

        query = self.recognizer.recognize_azure(audio, key=AZURE_SPEECH_KEY, location=AZURELOCATION)

        # remove if last character is not a letter
        while query and not query[-1].isalpha():
            query = query[:-1]

        try:
            self.query = "I think you said: " + query
            #process_query(query)
        except sr.UnknownValueError:
            self.query = "I did not understand what you said, please try again."
            #wait_keyword()
        except sr.RequestError as e:
            self.query = "Could not request results from the server; {0}".format(e)
            #wait_keyword()


class App(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.exit_btn = Button(self, text='Close', fg='white', bg='black', command=self.exit_app, height=4, width=18)
        self.update_btn = Button(self, text='Update', fg='white', bg='black', command="", height=4, width=18)
        self.report_btn = Button(self, text='Report', fg='white', bg='black', command="", height=4, width=18)
        self.search_btn = Button(self, text='Search', fg='white', bg='black', command=self.search, height=4, width=18)
        self.text_panel = Text(self, fg='white', bg='black', height=15, width=47)
        self.title("APC Smart Directory")
        self.attributes('-fullscreen', True)
        self.configure(background="white")
        self.resizable(False, False)
        self.create_btns()
        self.create_txt()
        self.start_listen()

    def create_btns(self):
        # Place Main Window Buttons
        self.search_btn.place(relx=0.45, rely=0.5, anchor=CENTER)
        self.report_btn.place(relx=0.55, rely=0.5, anchor=CENTER)
        self.update_btn.place(relx=0.45, rely=0.6, anchor=CENTER)
        self.exit_btn.place(relx=0.55, rely=0.6, anchor=CENTER)

    def create_txt(self):
        # System Output Panel
        text = 'Say "Hey RamNav to start searching..."'
        self.text_panel.configure(font=('DS-Digital', 11))
        self.text_panel.insert(END, text)
        self.text_panel.place(relx=0.5, rely=0.35, anchor=CENTER)
        self.text_panel.configure(state='disabled')

    def exit_app(self):
        self.destroy()

    def display_text(self, msg):
        self.text_panel.configure(state='normal')
        self.text_panel.delete('1.0', END)
        self.text_panel.insert(END, ''.join(msg))
        self.text_panel.configure(state='disabled')

    def search(self):
        self.display_text("Hi, which room/facility are you looking for?")
        time.sleep(1)
        self.start_query()

    def start_listen(self):
        recog_thread = AsyncRecog(speechsdk.KeywordRecognizer(),
                                  speechsdk.KeywordRecognitionModel("RamNav-Trigger.table"), "Hey RamNav")
        recog_thread.start()
        self.wait_key(recog_thread)

    def wait_key(self, thread):
        if thread.is_alive():
            # check the thread every 100ms
            self.after(100, lambda: self.wait_key(thread))
        else:
            thread.join()
            if thread.response:
                self.search()
            else:
                self.display_text("An error occured, try again")
                time.sleep(3)
                self.start_listen()

    def start_query(self):
        search_thread = SearchRm(listener, AZURE_SPEECH_KEY, AZURELOCATION)
        search_thread.start()
        self.get_query(search_thread)

    def get_query(self, thread):
        if thread.is_alive():
            self.after(100, lambda: self.get_query(thread))
        else:
            thread.join()
            self.display_text(thread.query)

    def report(self):
        self.display_text("Report Btn")

    def update(self):
        self.display_text("Update Btn")


# Instantiate RamNav App
if __name__ == "__main__":
    app = App()
    app.mainloop()


