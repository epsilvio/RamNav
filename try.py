import time
import wave

AZURE_SPEECH_KEY = "d2216ffb09af4c27ad2df097eb7f3cd3"
AZURELOCATION = "southeastasia"

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
            print("Hi, what room/facility are you looking for?")
            #get_query()

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
    #clear()
    result_future = keyword_recognizer.recognize_once_async(model)
    print('Say "Hey, RamNav!" to start searching...')
    result = result_future.get()

    # Read result audio (incl. the keyword).
    if result.reason == speechsdk.ResultReason.RecognizedKeyword:
        time.sleep(2)  # give some time so the stream is filled
        result_stream = speechsdk.AudioDataStream(result)
        result_stream.detach_input()  # stop any more data from input getting to the stream

        # save_future = result_stream.save_to_wav_file_async("AudioFromRecognizedKeyword.wav")
        # print('Saving file...')
        # saved = save_future.get()

    # If active keyword recognition needs to be stopped before results, it can be done with
    #
    #   stop_future = keyword_recognizer.stop_recognition_async()
    #   print('Stopping...')
    #   stopped = stop_future.get()

wait_keyword()