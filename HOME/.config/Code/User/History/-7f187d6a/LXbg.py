import os
import time
import azure.cognitiveservices.speech as speechsdk
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.text import TextTranslationClient

speech_key = "7fJr88MVZklBSl3vDoF7xkKxYtD9vrDYnXALYsoVbT6IG7b4F1NTJQQJ99BAAC5RqLJXJ3w3AAAYACOG0pi9"
service_region = "westeurope"
translator_key = "3iJ3P9yL1KJHkJKHFfQoq7zw2fr3PoH8LLYqd6y78bHSiNW4koxFJQQJ99BAAC5RqLJXJ3w3AAAbACOG807F"
translator_endpoint = "https://api.cognitive.microsofttranslator.com"
translator_region = "westeurope"

def make_output_dir(input_path):
    # The output directory is /home/basic/Projects/Vavilon/Translated-Audio + the name of the input directory with "-Translated" appended
    input_dir = os.path.dirname(input_path)
    input_file_name = os.path.basename(input_path)
    output_dir = input_dir.replace("Original-Audio", "Translated-Audio")
    output_path = os.path.join(output_dir, input_file_name.replace(".wav", "-Translated.wav"))

    return output_path



def transcribe_audio(file_path):

    if not speech_key or not service_region:
        print("Environment variables for Azure Speech service are not set.")
        return

    # Set up the speech configuration
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

    auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
        # Apperently the limit is 4 languages
        languages=[
            "en-US", 
            "sr-RS",
            "fr-FR",
            "de-DE"
        ]
    )

    #speech_config.speech_recognition_language = language

    # Set up the audio configuration
    audio_config = speechsdk.audio.AudioConfig(filename=file_path)

    # Create a speech recognizer
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        auto_detect_source_language_config=auto_detect_source_language_config,
        audio_config=audio_config
    )

    transcriptions = []
    detected_languages = []

    def recognised_callback(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            detected_language = evt.result.properties[
                speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult
            ]
            transcriptions.append(evt.result.text)
            detected_languages.append(detected_language)

            #print(f"Detected Language: {detected_language}")
            #print(f"Transcription: {evt.result.text}")
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized.")
        elif evt.result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = evt.result.cancellation_details
            print(f"Speech Recognition canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")


    # Connect the callback function to the recognized event
    speech_recognizer.recognized.connect(recognised_callback)

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

    # The detected language is the most often detected language
    detected_language = max(set(detected_languages), key=detected_languages.count)

    # Combine all recognized text segments
    full_transcription = " ".join(transcriptions)

    return full_transcription, detected_language
    

def translate_text(input_text, source_language, target_language):

    if not translator_key or not translator_region:
        raise ValueError("Azure Translator service key and region must be set as environment variables.")

    # Set up the Text Translation client
    credential = AzureKeyCredential(translator_key)
    text_translator = TextTranslationClient(credential=credential, region=translator_region)

    # Perform the translation
    response = text_translator.translate(
        body=[input_text],
        to_language=[target_language],
        from_language=source_language
    )

    # Extract the translated text from the response
    if response and response[0].translations:
        translated_text = response[0].translations[0].text
        return translated_text
    else:
        raise Exception("Translation failed. No response received.")
    

def synthesize_voice(input_text, language, output_path):
    
    if not speech_key or not service_region:
        raise ValueError("Azure Speech service key and region must be set as environment variables.")

    # Set up the speech configuration
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

    # Set up the voice synthesis configuration
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

    # Set up the voice synthesis parameters
    speech_synthesis_result = speech_synthesizer.speak_text_async(input_text).get()

    # Save the synthesized voice to a file
    speech_synthesis_result.write_to_wav_file(output_path)
    

if __name__ == "__main__":

    audio_file_path = "/home/basic/Projects/Vavilon/Original-Audio/Djokic-Outro-Serbian.wav"
    audio_file_path = "/home/basic/Projects/Vavilon/Original-Audio/test-audio-1.wav"
    output_path = make_output_dir(audio_file_path)
    print(f"Input path: {audio_file_path}")
    print(f"Output path: {output_path}")

    #Measure time elapsed
    start = time.time()

    transcription, input_language = transcribe_audio(audio_file_path)
    print(f"Detected language: {input_language}")
    print(f"Transcription: {transcription}\n\n")

    translated_text = translate_text(input_text=transcription, source_language=input_language, target_language="sr")

    synthesize_voice(translated_text, language="sr", output_path=output_path)

    print(f"Translation: {translated_text}")

    end = time.time()

    print(f"Time elapsed: {end - start}")
