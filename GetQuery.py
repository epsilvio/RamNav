import threading
import time
from tkinter import messagebox
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


AZURE_SPEECH_KEY = "d2216ffb09af4c27ad2df097eb7f3cd3"
AZURELOCATION = "southeastasia"
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
        self.uv = False
        self.re = False

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
        #while query and not query[-1].isalpha():
        #    query = query[:-1]

        try:
            self.query = "I think you said: " + query
        except sr.UnknownValueError:
            self.query = None
            self.uv = True
        except sr.RequestError as e:
            self.query = None
            self.re = True
