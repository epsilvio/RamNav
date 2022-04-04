import tkinter
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import json
import time
import requests
from io import BytesIO
import speech_recognition as sr
import ProcessQuery as PQ
import GetQuery as GQ

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
listener = sr.Recognizer()
file = open('wordbank.json')
wordbank = json.load(file)


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
        recog_thread = GQ.AsyncRecog(speechsdk.KeywordRecognizer(),
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
                time.sleep(2)
                self.start_listen()

    def start_query(self):
        search_thread = GQ.SearchRm(listener, AZURE_SPEECH_KEY, AZURELOCATION)
        search_thread.start()
        self.get_query(search_thread)

    def get_query(self, thread):
        if thread.is_alive():
            self.after(100, lambda: self.get_query(thread))
        else:
            thread.join()
            if thread.query is not None:
                self.display_text(thread.query)
                self.process_query(thread.query)
            else:
                if thread.uv:
                    self.display_text("I did not understand what you said. Try again.")
                    time.sleep(3)
                    self.start_listen()
                elif thread.re:
                    self.display_text("Server error. Try again.")
                    time.sleep(3)
                    self.start_listen()

    def process_query(self, query):
        pq_thread = PQ.ProcessQuery(query)
        pq_thread.start()
        self.get_choices(pq_thread)

    def get_choices(self, thread):
        if thread.is_alive():
            self.after(100, lambda: self.get_choices(thread))
        else:
            thread.join()
            if len(thread.result) > 1:
                self.show_choices(thread.result)
            elif len(thread.result) == 1:
                self.get_result(thread.result)
            elif len(thread.result) < 1:
                self.display_text("Your query returned no results. Try again.")
                time.sleep(3)
                self.start_listen()

    def get_result(self, room):
        gr_thread = PQ.ShowResult(room)
        gr_thread.start()
        self.show_result(gr_thread)

    def show_choices(self, choices):
        sc_thread = PQ.ShowChoices(choices)
        sc_thread.start()
        self.disp_choices(sc_thread)

    def disp_choices(self, thread):
        if thread.is_alive():
            self.after(100, lambda: self.disp_choices(thread))
        else:
            thread.join()
            if thread.msg is not None:
                self.display_text(thread.msg)
            else:
                self.display_text("An error occured. Try again.")
                time.sleep(3)
                self.start_listen()

    def show_result(self, thread):
        if thread.is_alive():
            self.after(100, lambda: self.show_result(thread))
        else:
            thread.join()
            if thread.result is not None:
                room = thread.result
                self.display_text("Room Name: " + str(room['Name']) + "\nRoom Number: " + str(room['Number'])
                                  + "\nFloor Level: " + str(room['Level']) + "\nImage Link: " + str(room['Link']))
                try:
                    response = requests.get(str(room['Link']))
                    img = Image.open(BytesIO(response.content))
                    img.show()
                except ValueError:
                    messagebox.showwarning("""No available image for this location!""")
            else:
                self.display_text("Your query returned no results. Try again.")
                time.sleep(3)
                self.start_listen()

    def report(self):
        self.display_text("Report Btn")

    def update(self):
        self.display_text("Update Btn")


# Instantiate RamNav App
if __name__ == "__main__":
    app = App()
    app.mainloop()
