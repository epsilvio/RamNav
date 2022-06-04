import tkinter
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import PIL
from PIL import ImageTk, Image
import time
import requests
from io import BytesIO
import ProcessQuery as PQ
import GetQuery as GQ
import PlayAudioResponse as PAR

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
screenW = 0
screenH = 0


class App(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.bg_photo = PhotoImage(file="assets/bg.png")
        self.btn_bg = [PhotoImage(file="assets/search.png"), PhotoImage(file="assets/report.png"),
                       PhotoImage(file="assets/exit.png")]
        self.disp_bg = [PhotoImage(file="assets/map.png"), PhotoImage(file="assets/qr.png"),
                        PhotoImage(file="assets/txtarea.png")]
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
        self.qr_panel.place(x=1200, y=100)
        self.create_btns()
        self.create_txt()
        self.show_defaults()
        time.sleep(2)
        self.wait_key()

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
        self.text_panel.place(x=221, y=570)
        self.text_panel.configure(state='disabled')

    def exit_app(self):
        self.get_audio("Good bye!")
        time.sleep(3)
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

    def get_audio(self, script):
        play_thread = PAR.ProcessAudio(script)
        play_thread.start()
        self.play_audio(play_thread)

    def play_audio(self, thread):
        if thread.is_alive():
            # check the thread every 100ms
            self.after(100, lambda: self.play_audio(thread))
        else:
            thread.join()

    def show_defaults(self):
        self.display_map('http://ramnav.westeurope.cloudapp.azure.com/images/map/placeholder.png')
        self.display_qr('http://ramnav.westeurope.cloudapp.azure.com/images/qr/placeholder.png')
        self.display_text('Say "Hey, RamNav!" to start searching...')
        self.get_audio('Say "Hey, RamNav!" to start searching')

    def search(self):
        self.display_text("Hi, which room/facility are you looking for?")
        self.get_audio("Hi! Which room or facility are you looking for?")
        time.sleep(1)
        self.start_query()

    def report(self):
        self.display_text("Report Btn")

    def update(self):
        self.display_text("Update Btn")

    def wait_key(self):
        thread = GQ.AsyncRecog(speechsdk.KeywordRecognizer(), speechsdk.KeywordRecognitionModel("RamNav-Trigger.table"),
                               "Hey RamNav")
        thread.start()
        self.listen_key(thread)

    def listen_key(self, thread):
        if thread.is_alive():
            # check the thread every 100ms
            self.after(100, lambda: self.listen_key(thread))
        else:
            thread.join()
            if thread.response:
                self.search()
            else:
                self.display_text("An error occured, try again.")
                self.get_audio("An error occured. Try again...")
                time.sleep(2)
                self.show_defaults()
                self.wait_key()

    def start_query(self):
        thread = GQ.SearchRm()
        thread.start()
        self.get_query(thread)

    def get_query(self, thread):
        if thread.is_alive():
            self.after(100, lambda: self.get_query(thread))
        else:
            thread.join()
            if thread.query is not None:
                self.display_text("Did you say: " + thread.query + "\n(Say Yes or No to confirm...)")
                self.get_audio("Did you say: " + thread.query + "... Say Yes or No to confirm")
                time.sleep(1)
                self.check_query(thread.query)

            else:
                if thread.uv:
                    self.display_text("I did not understand what you said. Try again.")
                    self.get_audio("I did not understand what you said. Try again.")
                    time.sleep(2)
                    self.show_defaults()
                    self.wait_key()
                elif thread.re:
                    self.display_text("Server error. Try again.")
                    self.get_audio("Server error. Try again.")
                    time.sleep(2)
                    self.show_defaults()
                    self.wait_key()

    def check_query(self, query):
        thread = GQ.VerifyQuery(query)
        thread.start()
        self.verify_query(thread)

    def verify_query(self, thread):
        if thread.is_alive():
            self.after(100, lambda: self.verify_query(thread))
        else:
            thread.join()
            if thread.confirm:
                self.get_audio("Query Confirmed!")
                #self.process_query(thread.query)
            else:
                self.display_text("Query not confirmed. Try querying again.")
                time.sleep(2)
                #self.show_defaults()
                #self.wait_key()

    def process_query(self, query):
        thread = PQ.ProcessQuery(query)
        thread.start()
        self.check_choice(thread)

    def check_choice(self, thread):
        if thread.is_alive():
            self.after(100, lambda: self.check_choice(thread))
        else:
            thread.join()
            if len(thread.result) > 1:
                if len(thread.result) > 3:
                    self.display_text("Your query returned too many possible results. Please try to rephrase your query.")
                    self.get_audio("Your query returned too many possible results. Please try to rephrase your query.")
                    time.sleep(2)
                    self.show_defaults()
                    #self.wait_key()
                else:
                    self.display_text("Showing Choices")
                    #self.get_options(thread.result)
            elif len(thread.result) == 1:
                self.display_text("One Result")
                #self.get_result(thread.result)
            elif len(thread.result) < 1:
                self.display_text("Your query returned no results.\nPlease try to rephrase your query.")
                self.get_audio("Your query returned no results. Please try to rephrase your query.")
                self.after(2000, lambda: self.show_defaults(), self.wait_key())
                #time.sleep(2)
                #self.show_defaults()
                #self.wait_key()

    #def get_options(self):


# Instantiate RamNav App
if __name__ == "__main__":
    app = App()
    app.mainloop()
