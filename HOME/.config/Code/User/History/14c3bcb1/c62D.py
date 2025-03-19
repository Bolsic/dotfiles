import azure.cognitiveservices.speech as speechsdk
import os

speech_key = "7fJr88MVZklBSl3vDoF7xkKxYtD9vrDYnXALYsoVbT6IG7b4F1NTJQQJ99BAAC5RqLJXJ3w3AAAYACOG0pi9"
service_region = "westeurope"

print(speech_key, service_region)

# Specify the path to your audio file
audio_filename = "/home/basic/Downloads/OSR_us_000_0010_8k.wav"

# Create a speech configuration
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# Create an audio configuration from the audio file
audio_config = speechsdk.audio.AudioConfig(filename=audio_filename)

# Create a speech recognizer
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

# Define a callback function to handle recognized results
def recognized_callback(evt):
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"Recognized: {evt.result.text}")
    elif evt.result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized.")
    elif evt.result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = evt.result.cancellation_details
        print(f"Speech Recognition canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")

# Connect the callback function to the recognized event
speech_recognizer.recognized.connect(recognized_callback)

# Start continuous recognition
speech_recognizer.start_continuous_recognition()

# Keep the program running until recognition is complete

# Stop continuous recognition
speech_recognizer.stop_continuous_recognition()
