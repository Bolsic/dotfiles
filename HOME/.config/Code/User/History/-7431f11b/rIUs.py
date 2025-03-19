import os
import requests
import uuid
import azure.cognitiveservices.speech as speechsdk

# Create a function that creates the path to the output udio file
# Output aduio file will be saved in the same directory /home/basic/Projects/Vavilon/Translated-Audio
# Input audio files are located at /home/basic/Projects/Vavilon/Original-Audio/  
# and will be named as the input file but have the "Translated-" prefix
def create_output_audio_path(input_audio_path):   
    input_audio_dir = os.path.dirname(input_audio_path)
    output_dir = os.path.join(os.path.dirname(input_audio_path).split("Original-Audio")[0], "Translated-Audio")
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.basename(input_audio_path)
    output_filename = "Translated-" + output_filename
    output_path = os.path.join(output_dir, output_filename)
    return output_path

import azure.cognitiveservices.speech as speechsdk

def transcribe_audio_to_text(audio_path):
    # Initialize speech configuration
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    audio_config = speechsdk.audio.AudioConfig(filename=audio_path)

    # Define the list of potential source languages in BCP-47 format
    auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
        languages=["en-US", "sr-RS", "fr-FR", "de-DE", "it-IT"]  # English, Serbian, French, German, Italian
    )

    # Create the speech recognizer with auto language detection
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config,
        auto_detect_source_language_config=auto_detect_source_language_config
    )

    # List to hold the recognized text segments
    recognized_texts = []
    detected_language = None

    # Function to handle recognized results
    def recognized_callback(evt):
        nonlocal detected_language
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            recognized_texts.append(evt.result.text)
            if detected_language is None:
                # Retrieve the detected language once
                auto_detect_result = speechsdk.AutoDetectSourceLanguageResult(evt.result)
                detected_language = auto_detect_result.language
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized.")
        elif evt.result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = evt.result.cancellation_details
            print(f"Speech Recognition canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")
                print(f"Error code: {cancellation_details.error_code}")


    # Connect the callback function to the recognized event
    speech_recognizer.recognized.connect(recognized_callback)

    # Start continuous recognition
    speech_recognizer.start_continuous_recognition()

    # Wait for completion
    speech_recognizer.session_started.connect(lambda evt: print("Session started."))
    speech_recognizer.session_stopped.connect(lambda evt: print("Session stopped."))
    speech_recognizer.canceled.connect(lambda evt: print(f"Canceled: {evt}"))

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
    transcribed_text = " ".join(recognized_texts)

    return transcribed_text, detected_language

def translate_text(text, target_language, source_language):
    path = '/translate'
    constructed_url = translator_endpoint + path

    params = {
        'api-version': '3.0',
        'from': source_language,  # Specify the source language
        'to': target_language
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

def synthesize_text_to_speech(text, output_path, language):
    # Initialize speech configuration
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    
    # Set the voice name based on the target language
    voice_name = {
        'en': 'en-US-JennyNeural',
        'sr': 'sr-RS-NicholasNeural',
        'fr': 'fr-FR-DeniseNeural',
        'de': 'de-DE-ConradNeural',
        'it': 'it-IT-DiegoNeural'
    }.get(language, 'en-US-JennyNeural')  # Default to English if language not found
    
    speech_config.speech_synthesis_voice_name = voice_name
    
    # Set the audio output configuration
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
    
    # Create the speech synthesizer
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    
    # Synthesize the text to speech
    result = synthesizer.speak_text_async(text).get()
    
    # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Audio content written to file: {output_path}")
    else:
        raise Exception(f"Speech synthesis failed: {result.reason}")

def main(input_audio_path):

    # Check if the file exists
    if not os.path.isfile(input_audio_path):
        print("The specified audio file does not exist.")
        return

    # Prompt user for target language code
    target_language = input("Enter the target language code (e.g., 'en' for English, 'sr' for Serbian, 'fr' for French, 'de' for German, 'it' for Italian): ").strip()

    # Transcribe the audio file
    print("Transcribing audio...")
    transcribed_text, detected_language = transcribe_audio_to_text(input_audio_path)
    print(f"Detected Language: {detected_language}")
    print(f"Transcribed Text: {transcribed_text}")

    # Translate the transcribed text
    print("Translating text...")
    translated_text = translate_text(transcribed_text, target_language, detected_language)
    print(f"Translated Text: {translated_text}")

    # Synthesize the translated text to speech
    output_audio_path = create_output_audio_path(input_audio_path)
    print("Output audio path:", output_audio_path)

    print("Synthesizing translated text to speech...")
    synthesize_text_to_speech(translated_text, output_audio_path, target_language)
    print("Speech synthesis complete.")

# Set up your Azure subscription information
speech_key = "7fJr88MVZklBSl3vDoF7xkKxYtD9vrDYnXALYsoVbT6IG7b4F1NTJQQJ99BAAC5RqLJXJ3w3AAAYACOG0pi9"
service_region = "westeurope"
translator_key = "1nIGXkVx5zPFhSkcH0UwLOs3qMY4Il8RQ2sytyZLL46VZDgF0IEXJQQJ99BAAC5RqLJXJ3w3AAAbACOGr1dp"
translator_endpoint = "https://api.cognitive.microsofttranslator.com"

# Path to the input English audio file and the output Serbian audio file
input_audio_path = "/home/basic/Projects/Vavilon/Original-Audio/Djokic-Outro-Serbian.wav"


main(input_audio_path)
