import os
import requests
import uuid
import azure.cognitiveservices.speech as speechsdk

# Set up your Azure subscription information
speech_key = "7fJr88MVZklBSl3vDoF7xkKxYtD9vrDYnXALYsoVbT6IG7b4F1NTJQQJ99BAAC5RqLJXJ3w3AAAYACOG0pi9"
service_region = "westeurope"
translator_key = "1nIGXkVx5zPFhSkcH0UwLOs3qMY4Il8RQ2sytyZLL46VZDgF0IEXJQQJ99BAAC5RqLJXJ3w3AAAbACOGr1dp"
translator_endpoint = "https://api.cognitive.microsofttranslator.com"

# Path to the input English audio file and the output Serbian audio file
input_audio_path = "/home/basic/Projects/Vavilon/Interview-English.wav"
output_audio_path = "/home/basic/Projects/Vavilon/test-prevod-1.wav"

# Function to transcribe English audio to text
def transcribe_audio_to_text(audio_path):
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    # List to hold the recognized text segments
    recognized_texts = []

    def recognized_callback(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            recognized_texts.append(evt.result.text)
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

    # Wait until the recognition is complete
    done = False
    def stop_cb(evt):
        nonlocal done
        done = True

    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    while not done:
        pass

    # Stop continuous recognition
    speech_recognizer.stop_continuous_recognition()

    # Combine all recognized text segments
    return " ".join(recognized_texts)

# Function to translate text to Serbian
def translate_text_to_serbian(text):
    path = '/translate'
    constructed_url = translator_endpoint + path

    params = {
        'api-version': '3.0',
        'to': 'sr'  # Serbian language code
    }

    headers = {
        'Ocp-Apim-Subscription-Key': translator_key,
        'Ocp-Apim-Subscription-Region': service_region,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    body = [{'text': text}]
    response = requests.post(constructed_url, params=params, headers=headers, json=body)
    response.raise_for_status()
    translation = response.json()
    return translation[0]['translations'][0]['text']

# Function to synthesize Serbian text to speech and save to a file
def synthesize_text_to_speech(text, output_path):
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    result = synthesizer.speak_text_async(text).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Audio content written to file: {output_path}")
    else:
        raise Exception(f"Speech synthesis failed: {result.reason}")

# Main workflow
try:
    # Step 1: Transcribe English audio to text
    print("Transcribing English audio to text...")
    english_text = transcribe_audio_to_text(input_audio_path)
    print(f"Transcribed Text: {english_text}")

    # Step 2: Translate English text to Serbian
    print("Translating text to Serbian...")
    serbian_text = translate_text_to_serbian(english_text)
    print(f"Translated Text: {serbian_text}")

    # Step 3: Synthesize Serbian text to speech
    print("Synthesizing Serbian text to speech...")
    synthesize_text_to_speech(serbian_text, output_audio_path)
    print("Process completed successfully.")

except Exception as e:
    print(f"An error occurred: {e}")
