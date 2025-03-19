import azure.cognitiveservices.speech as speechsdk
import os

speech_key = "e50ab69c-4af3-4382-b2d2-a066671f2cb9"
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

# Perform speech recognition
result = speech_recognizer.recognize_once()

# Check the result
if result.reason == speechsdk.ResultReason.RecognizedSpeech:
    print("Recognized: {}".format(result.text))
elif result.reason == speechsdk.ResultReason.NoMatch:
    print("No speech could be recognized: {}".format(result.no_match_details))
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result.cancellation_details
    print("Speech Recognition canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        print("Error details: {}".format(cancellation_details.error_details))
