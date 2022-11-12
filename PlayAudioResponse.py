import azure.cognitiveservices.speech as speechsdk
import threading

# Creates an instance of a speech config with specified subscription key and service region.
speech_key = "[AZURE-PRIVATE-KEY]"
service_region = "[SERVER-REGION]"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
# Note: the voice setting will not overwrite the voice element in input SSML.
speech_config.speech_synthesis_voice_name = "en-AU-WilliamNeural"


class ProcessAudio(threading.Thread):
    def __init__(self, script):
        super(ProcessAudio, self).__init__()
        self.text = script
        # use the default speaker as audio output.
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        self.result = None

    def run(self):
        self.result = self.speech_synthesizer.speak_text_async(self.text).get()
        self.text = None
        # Check result
        """if self.result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(self.text))
        elif self.result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = self.result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))"""


