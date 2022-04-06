import tkinter
from tkinter import *
import threading


class ChoicePopup(threading.Thread, tkinter.Tk):
    def __init__(self, set):
        super(ChoicePopup, self).__init__()
        self.choices = set
        self.btns = None
        self.base_width = 100
        self.base_height = 20
        for i in len(set):
            self.base_height += 20
        self.geometry(str(self.base_width) + "x" + str(self.base_height))
        self.title("Which room do you choose?")

    def create_btns(self):
        for i in len(set):
            self.btns[i] = Button(self, text='Sample', fg='white', bg='black', command=self.exit_app, height=4, width=18)
