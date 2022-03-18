from tkinter import *
from tkinter import ttk, filedialog, messagebox
import PIL
from PIL import Image, ImageTk
import speech_recognition as sr
import json
import pyodbc
import requests
from io import BytesIO
from time import sleep
import os
import time
import main as logic

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

# Create Main Window
root = Tk()
root.title("APC Smart Directory")
root.attributes('-fullscreen', True)
root.configure(background="white")
root.resizable(False, False)


def exit_app():
    root.destroy()


def display_text(msg):
    text_panel.configure(state='normal')
    text_panel.delete('1.0', END)
    text_panel.insert(END, ''.join(msg))
    text_panel.configure(state='disabled')


def search():
    resp = logic.wait_keyword()
    display_text(resp)


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
            time.sleep(0.5)

        nonlocal done
        done = True

    def canceled_cb(evt):
        result = evt.result
        if result.reason == speechsdk.ResultReason.Canceled:
            display_text('Keyword Waiting Canceled')
        nonlocal done
        done = True

    # Connect callbacks to the events fired by the keyword recognizer.
    keyword_recognizer.recognized.connect(recognized_cb)
    keyword_recognizer.canceled.connect(canceled_cb)
    # Start keyword recognition.
    # clear()
    result_future = keyword_recognizer.recognize_once_async(model)
    display_text('Say "Hey, RamNav!" to start searching...')
    result = result_future.get()
    # Read result audio (incl. the keyword).
    if result.reason == speechsdk.ResultReason.RecognizedKeyword:
        time.sleep(2)  # give some time so the stream is filled
        result_stream = speechsdk.AudioDataStream(result)
        result_stream.detach_input()  # stop any more data from input getting to the stream
        # get_query()


# Main Window Buttons
search_btn = Button(root, text='Search', fg='white', bg='black', command=wait_keyword, height=4, width=18)
search_btn.place(relx=0.45, rely=0.5, anchor=CENTER)
report_btn = Button(root, text='Report', fg='white', bg='black', command="", height=4, width=18)
report_btn.place(relx=0.55, rely=0.5, anchor=CENTER)
update_btn = Button(root, text='Update', fg='white', bg='black', command="", height=4, width=18)
update_btn.place(relx=0.45, rely=0.6, anchor=CENTER)
exit_btn = Button(root, text='Close', fg='white', bg='black', command=exit_app, height=4, width=18)
exit_btn.place(relx=0.55, rely=0.6, anchor=CENTER)

# System Output Panel
text_panel = Text(root, fg='white', bg='black', height=15, width=47)
text = '[No Text Displayed]'
text_panel.configure(font=('DS-Digital', 11))
text_panel.insert(END, text)
text_panel.place(relx=0.5, rely=0.35, anchor=CENTER)
text_panel.configure(state='disabled')

# Instantiate RamNav App
root.mainloop()
