"""import mysql.connector

mydb = mysql.connector.connect(
    host="20.101.71.189",
    user="azureuser",
    password="ramnav",
    database="ramnav-db"
)

mycursor = mydb.cursor()

mycursor.execute("SELECT * FROM Rooms")

myresult = mycursor.fetchall()

for x in myresult:
    print(x)

mydb.close()

import requests

file = requests.get('http://ramnav.westeurope.cloudapp.azure.com/js/dictionary.json')
wordbank = file.json()
txt = ("Where can I play basketball")
counter = 0
rooms = []

for key1 in wordbank.keys():
    for key2 in wordbank[key1][0].keys():
        if wordbank[key1][0][key2].lower() in txt.lower():
            counter += 1
            room_id = key1
            rooms.append(room_id)
            break
print(wordbank)
#print(wordbank['215'][0]['keyword1'].lower() in txt.lower())"""

'''
  For more samples please visit https://github.com/Azure-Samples/cognitive-services-speech-sdk 
'''

import azure.cognitiveservices.speech as speechsdk

# Creates an instance of a speech config with specified subscription key and service region.
speech_key = "f048a4008e8344a3a92f289da20f2738"
service_region = "southeastasia"

speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
# Note: the voice setting will not overwrite the voice element in input SSML.
speech_config.speech_synthesis_voice_name = "en-AU-WilliamNeural"

with open('script.txt', 'r') as file:
    data = file.read().replace('\n', '')

text = "Hello, I am RamNav!"

# use the default speaker as audio output.
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

result = speech_synthesizer.speak_text_async(data).get()
# Check result
if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesized for text [{}]".format(text))
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result.cancellation_details
    print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        print("Error details: {}".format(cancellation_details.error_details))

