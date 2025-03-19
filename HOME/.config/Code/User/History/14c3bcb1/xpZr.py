import azure.cognitiveservices.speech as speechsdk
import os
import time

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

# Define a flag to indicate when recognition has stopped
done = False

# Define event handlers
def stop_cb(evt):
    """Callback that signals to stop continuous recognition upon receiving a session stopped event."""
    print('CLOSING on {}'.format(evt))
    global done
    done = True

def recognized_cb(evt):
    """Callback that prints recognized results."""
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(evt.result.text))
    elif evt.result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized.")
    elif evt.result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = evt.result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

# Connect event handlers
speech_recognizer.recognized.connect(recognized_cb)
speech_recognizer.session_stopped.connect(stop_cb)
speech_recognizer.canceled.connect(stop_cb)

# Start continuous recognition
speech_recognizer.start_continuous_recognition()

# Wait until the recognition is complete
while not done:
    time.sleep(0.5)

# Stop continuous recognition
speech_recognizer.stop_continuous_recognition()
