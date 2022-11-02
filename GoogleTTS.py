from google.cloud import texttospeech
from playsound import playsound
import os
import threading

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'ramnav-tts-key.json'

# Instantiates a client
client = texttospeech.TextToSpeechClient()


class ProcessResponse(threading.Thread):
    def __init__(self, script):
        super(ProcessResponse, self).__init__()
        self.text = script
        # Set the text input to be synthesized
        self.synthesis_input = texttospeech.SynthesisInput(text=self.text)
        # Build the voice request, select the language code ("en-US") and the ssml
        # voice gender ("neutral")
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        # Select the type of audio file you want returned
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        self.result = None

    def run(self):
        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        self.result = client.synthesize_speech(
            input=self.synthesis_input, voice=self.voice, audio_config=self.audio_config
        )
        if os.path.isfile('gc-tts.mp3'):
            os.remove('gc-tts.mp3')
        # The response's audio_content is binary.
        with open("gc-tts.mp3", "wb") as out:
            # Write the response to the output file.
            out.write(self.result.audio_content)

        #Play the audio file
        playsound('gc-tts.mp3')
