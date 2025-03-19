import os
import time
import threading
import json
import azure.cognitiveservices.speech as speechsdk
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.text import TextTranslationClient

speech_key = "8DWayvEHZerwdy1oXOhSMJRQJ2ic0boQIkoVo6BhVwbHMDGRnLiiJQQJ99BBAC5RqLJXJ3w3AAAYACOGKpnv"
service_region = "westeurope"
translator_key = "8uzkNOPtkQURJWrm2Zxih0R0NpHJ36rXNoVUG9226ZJ2Yx6pMcLSJQQJ99BBAC5RqLJXJ3w3AAAbACOGpome"
translator_region = "westeurope"
translator_endpoint = "https://api.cognitive.microsofttranslator.com"

# Set your Azure keys and regions here
speech_key = "YOUR_SPEECH_KEY"
service_region = "YOUR_SPEECH_REGION"
translator_key = "YOUR_TRANSLATOR_KEY"
translator_region = "YOUR_TRANSLATOR_REGION"

# Global list to collect recognized text segments
transcription_results = []

# Event to signal when recognition has finished
done_event = threading.Event()

def make_output_dir(input_path):
    # Replace "Test-Audio" with "Test-Output" and add "-Translated.wav" to filename
    input_dir = os.path.dirname(input_path)
    input_file_name = os.path.basename(input_path)
    output_dir = input_dir.replace("Test-Audio", "Test-Output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, input_file_name.replace(".wav", "-Translated.wav"))
    return output_path

def pick_file_interface(directory):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    print("Files in the directory:")
    for idx, file in enumerate(files, start=1):
        print(f"{idx}. {file}")
    try:
        choice = int(input("Enter the number of the file you want to use: "))
        if 1 <= choice <= len(files):
            selected_file = files[choice - 1]
            print(f"You have selected: {selected_file}\n")
            audio_file_path = os.path.join(directory, selected_file)
            return audio_file_path
        else:
            print("Invalid selection. Exiting.")
            exit(1)
    except ValueError:
        print("Invalid input. Exiting.")
        exit(1)

def pick_language_interface():
    print("Select target language for translation:")
    print("1. English (en-US)")
    print("2. Serbian (sr-RS)")
    print("3. French (fr-FR)")
    print("4. Italian (it-IT)")
    try:
        choice = int(input("Enter the number of the language: "))
        languages = {1: "en-US", 2: "sr-RS", 3: "fr-FR", 4: "it-IT"}
        if choice in languages:
            selected_language = languages[choice]
            print(f"You have selected: {selected_language}\n")
            return selected_language
        else:
            print("Invalid selection. Exiting.")
            exit(1)
    except ValueError:
        print("Invalid input. Exiting.")
        exit(1)

def recognized_callback(evt):
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"Recognized: {evt.result.text}")
        transcription_results.append(evt.result.text)
    elif evt.result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = evt.result.cancellation_details
        print(f"Speech Recognition canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")

def stop_callback(evt):
    print("Session stopped, setting done_event.")
    done_event.set()

def run_recognition(file_path):
    # Use auto-detect for a few languages
    auto_detect_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
        languages=["en-US", "sr-RS", "fr-FR", "it-IT"]
    )
    audio_config = speechsdk.audio.AudioConfig(filename=file_path)
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        auto_detect_source_language_config=auto_detect_config,
        audio_config=audio_config
    )
    
    recognizer.recognized.connect(recognized_callback)
    recognizer.session_stopped.connect(stop_callback)
    recognizer.canceled.connect(stop_callback)

    recognizer.start_continuous_recognition()
    # Wait until done_event is set (i.e. recognition session ended)
    done_event.wait()
    recognizer.stop_continuous_recognition()

def translate_text(input_text, source_language, target_language):
    if not translator_key or not translator_region:
        raise ValueError("Translator key/region must be set.")
    credential = AzureKeyCredential(translator_key)
    text_translator = TextTranslationClient(credential=credential, region=translator_region)
    response = text_translator.translate(
        body=[input_text],
        to_language=[target_language],
        from_language=source_language
    )
    if response and response[0].translations:
        translated_text = response[0].translations[0].text
        return translated_text
    else:
        raise Exception("Translation failed. No response received.")

def synthesize_voice(input_text, language, output_path):
    if not speech_key or not service_region:
        raise ValueError("Speech key/region must be set.")
    # Set the synthesis language and choose a voice
    speech_config.speech_synthesis_language = language
    if language == "en-US":
        voice = "en-US-PhoebeNeural"
    elif language == "sr-RS":
        voice = "sr-RS-NicholasNeural"
    elif language == "fr-FR":
        voice = "fr-FR-DeniseNeural"
    elif language == "it-IT":
        voice = "it-IT-IsabellaNeural"
    else:
        print("Invalid language for synthesis.")
        return
    speech_config.speech_synthesis_voice_name = voice
    audio_output = speechsdk.audio.AudioOutputConfig(filename=output_path)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output)
    result = synthesizer.speak_text_async(input_text).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Audio synthesized and saved to: {output_path}")
    else:
        print("Speech synthesis failed.")

if __name__ == "__main__":
    # Directory containing input audio files
    directory_path = "/home/basic/Projects/Original-Audio"
    audio_file_path = pick_file_interface(directory_path)
    target_language = pick_language_interface()
    output_path = make_output_dir(audio_file_path)
    print(f"Input file: {audio_file_path}")
    print(f"Output file will be: {output_path}\n")

    # Create global speech configuration
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    # (Optional: set additional properties on speech_config here if needed)

    # Start the transcription in a separate thread
    recognition_thread = threading.Thread(target=run_recognition, args=(audio_file_path,))
    recognition_thread.start()
    recognition_thread.join()

    # Combine the recognized text segments into one string
    full_transcription = " ".join(transcription_results)
    print(f"\nFull Transcription:\n{full_transcription}\n")

    # For simplicity, assume the source language is the first one detected, e.g. "en-US"
    source_language = "en-US"  # In a real scenario, you might derive this from the recognized properties

    # Translate the transcription
    print("Translating text...")
    translated_text = translate_text(full_transcription, source_language, target_language)
    print(f"Translated Text:\n{translated_text}\n")

    # Synthesize the translated text into an audio file
    print("Synthesizing voice...")
    synthesize_voice(translated_text, target_language, output_path)
    print("Process completed.")
