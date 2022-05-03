import tkinter
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import PIL
from PIL import ImageTk, Image
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

# GLOBAL VARIABLES
AZURE_SPEECH_KEY = "d2216ffb09af4c27ad2df097eb7f3cd3"
AZURELOCATION = "southeastasia"
listener = sr.Recognizer()
file = open('wordbank.json')
wordbank = json.load(file)
screenW = 0
screenH = 0



class App(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.bg_photo = PhotoImage(file="assets/bg.png")
        self.btn_bg = [PhotoImage(file="assets/search.png"), PhotoImage(file="assets/report.png"), PhotoImage(file="assets/exit.png")]
        self.disp_bg = [PhotoImage(file="assets/map.png"), PhotoImage(file="assets/qr.png"), PhotoImage(file="assets/txtarea.png")]
        self.title("RamNav: APC Smart Directory")
        self.attributes('-fullscreen', True)
        self.configure(background="white")
        self.resizable(False, False)
        screenW = self.winfo_screenwidth()
        screenH = self.winfo_screenheight()
        self.bg_label = Label(self, image=self.bg_photo)
        self.search_label = Label(self, image=self.btn_bg[0])
        self.report_label = Label(self, image=self.btn_bg[1])
        self.exit_label = Label(self, image=self.btn_bg[2])
        self.map_label = Label(self, image=self.disp_bg[0])
        self.qr_label = Label(self, image=self.disp_bg[1])
        self.txtarea_label = Label(self, image=self.disp_bg[2])
        self.exit_btn = Button(self, image=self.btn_bg[2], fg='white', command=self.exit_app, borderwidth=0)
        self.report_btn = Button(self, image=self.btn_bg[1], fg='white', command="", borderwidth=0)
        self.search_btn = Button(self, image=self.btn_bg[0], fg='white', command=self.search, borderwidth=0)
        self.text_panel = Text(self, fg='black', bg='#669DB3', height=4, width=61, borderwidth=0)
        self.map_panel = Label(self, image=self.disp_bg[0], borderwidth=0)
        self.qr_panel = Label(self, image=self.disp_bg[1], borderwidth=0)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.map_panel.place(x=221, y=100)
        self.qr_panel.place(x=1100, y=100)
        self.create_btns()
        self.create_txt()
        self.display_map('http://ramnav.westeurope.cloudapp.azure.com/images/map/placeholder.png')
        self.display_qr('http://ramnav.westeurope.cloudapp.azure.com/images/qr/placeholder.png')
        self.start_listen()

    def create_btns(self):
        # Place Main Window Buttons
        self.search_btn.place(relx=0.2, rely=0.8, anchor=CENTER)
        self.report_btn.place(relx=0.5, rely=0.8, anchor=CENTER)
        self.exit_btn.place(relx=0.8, rely=0.8, anchor=CENTER)

    def create_txt(self):
        # System Output Panel
        text = 'Say "Hey RamNav to start searching..."'
        self.text_panel.configure(font=('DS-Digital', 20))
        self.text_panel.insert(END, text)
        self.text_panel.place(x=221, y=590)
        self.text_panel.configure(state='disabled')

    def exit_app(self):
        self.destroy()

    def display_text(self, msg):
        self.text_panel.configure(state='normal')
        self.text_panel.delete('1.0', END)
        self.text_panel.insert(END, ''.join(msg))
        self.text_panel.configure(state='disabled')

    def display_map(self, link):
        try:
            response = requests.get(link)
            self.map_img = Image.open(BytesIO(response.content))
            self.map_img = self.map_img.resize((800, 450), Image.ANTIALIAS)
            self.map_img = ImageTk.PhotoImage(self.map_img)
            self.map_panel.configure(image=self.map_img)
            self.map_panel.image = self.map_img
        except (PIL.UnidentifiedImageError, AttributeError):
            messagebox.showwarning("Warning", "No/Invalid file selected")

    def display_qr(self, link):
        try:
            response = requests.get(link)
            self.qr_img = Image.open(BytesIO(response.content))
            self.qr_img = self.qr_img.resize((600, 600), Image.ANTIALIAS)
            self.qr_img = ImageTk.PhotoImage(self.qr_img)
            self.qr_panel.configure(image=self.qr_img)
            self.qr_panel.image = self.qr_img
        except (PIL.UnidentifiedImageError, AttributeError):
            messagebox.showwarning("Warning", "No/Invalid file selected")

    def search(self):
        self.display_text("Hi, which room/facility are you looking for?")
        time.sleep(1)
        self.start_query()

    def show_defaults(self):
        self.display_map('http://ramnav.westeurope.cloudapp.azure.com/images/map/placeholder.png')
        self.display_qr('http://ramnav.westeurope.cloudapp.azure.com/images/qr/placeholder.png')

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
                self.display_text("An error occured, try again.\n\nSay 'Hey, RamNav' to start searching.")
                time.sleep(3)
                self.show_defaults()
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
                time.sleep(3)
                self.process_query(thread.query)
            else:
                if thread.uv:
                    self.display_text("I did not understand what you said. Try again.")
                    time.sleep(3)
                    self.show_defaults()
                    self.start_listen()
                elif thread.re:
                    self.display_text("Server error. Try again. \n\nSay 'Hey, RamNav' to start searching.")
                    time.sleep(3)
                    self.show_defaults()
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
                if len(thread.result) > 3:
                    self.display_text("Your query returned too many possible results. Please try to rephrase your query.\n\nSay 'Hey, RamNav' to start searching.")
                    self.show_defaults()
                    self.start_listen()
                else:
                    self.show_choices(thread.result)
            elif len(thread.result) == 1:
                self.get_result(thread.result)
            elif len(thread.result) < 1:
                self.display_text("Your query returned no results. Please try to rephrase your query.\n\nSay 'Hey, RamNav' to start searching.")
                time.sleep(3)
                self.show_defaults()
                self.start_listen()

    def ask_choice(self, ids):
        ak_thread = PQ.GetChoice(listener, AZURE_SPEECH_KEY, AZURELOCATION, ids)
        ak_thread.start()
        self.get_choice(ak_thread)

    def get_choice(self, thread):
        if thread.is_alive():
            self.after(100, lambda: self.get_choice(thread))
        else:
            thread.join()
            if thread.response is not None:
                self.display_text(thread.response)
                time.sleep(3)
                if thread.choice is not None:
                    self.display_text("\nGetting info of Room " + thread.choice[0])
                    self.get_result(thread.choice)
                else:
                    self.start_listen()
            else:
                if thread.uv:
                    self.display_text("Unknown Value Error Occured. Please query again.\n\nSay 'Hey, RamNav' to start searching.")
                    self.show_defaults()
                    self.start_listen()
                elif thread.re:
                    self.display_text("Request Error Occured. Please query again.\n\nSay 'Hey, RamNav' to start searching.")
                    self.show_defaults()
                    self.start_listen()
                elif thread.ie:
                    self.display_text("Invalid choice. Please query again.\n\nSay 'Hey, RamNav' to start searching.")
                    self.show_defaults()
                    self.start_listen()

    def show_choices(self, choices):
        sc_thread = PQ.ShowChoices(choices)
        sc_thread.start()
        self.disp_choices(sc_thread, choices)

    def disp_choices(self, thread, choices):
        if thread.is_alive():
            self.after(100, lambda: self.disp_choices(thread))
        else:
            thread.join()
            if thread.msg is not None:
                self.display_text(thread.msg)
                time.sleep(3)
                self.ask_choice(choices)
            else:
                self.display_text("An error occured. Try again.")
                time.sleep(3)
                self.show_defaults()
                self.start_listen()

    def get_result(self, room):
        gr_thread = PQ.ShowResult(room)
        gr_thread.start()
        self.show_result(gr_thread)

    def show_result(self, thread):
        if thread.is_alive():
            self.after(100, lambda: self.show_result(thread))
        else:
            thread.join()
            if thread.result is not None:
                room = thread.result
                self.display_text("The " + str(room['Name']) + " is at the " + str(room['Level']) + " Floor.\n\nSay 'Hey RamNav!' to start searching again.")
                self.display_map(str(room['Map-Link']))
                self.display_qr(str(room['QR-Link']))
                self.start_listen()
            else:
                self.display_text("Your query returned no results. Please try to rephrase your query.\n\nSay 'Hey, RamNav' to start searching.")
                time.sleep(3)
                self.show_defaults()
                self.start_listen()

    def report(self):
        self.display_text("Report Btn")

    def update(self):
        self.display_text("Update Btn")


# Instantiate RamNav App
if __name__ == "__main__":
    app = App()
    app.mainloop()
