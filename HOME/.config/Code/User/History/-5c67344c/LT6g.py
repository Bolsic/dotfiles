import os
import time
import threading
import queue
import azure.cognitiveservices.speech as speechsdk
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.text import TextTranslationClient

def translate_audio_file(audio_file_path, target_language, speech_key, speech_region):#, source_language="en-US"):
    # Create a translation configuration using your subscription info
    translation_config = speechsdk.translation.SpeechTranslationConfig(
        subscription=speech_key, region=speech_region)
    
    auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
        # Apperently the limit is 4 languages
        languages=[
            "en-US", 
            #"sr-RS",
            "fr-FR",
            "it-IT"
        ]
    )
    
    # Set the source language for recognition
    #translation_config.speech_recognition_language = source_language
    
    # Add the target language for translation
    translation_config.add_target_language(target_language)
    
    # Specify the audio input from a file
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
    
    # Create the TranslationRecognizer with the given config and audio input
    recognizer = speechsdk.translation.TranslationRecognizer(
        translation_config=translation_config,
        auto_detect_source_language_config=auto_detect_source_language_config,
        audio_config=audio_config)
    
    # Perform the recognition and translation (synchronously)
    result = recognizer.recognize_once_async().get()
    
    # Check the result and return the translated text
    if result.reason == speechsdk.ResultReason.TranslatedSpeech:
        recognized_text = result.text
        translated_text = result.translations[target_language]
        print("Recognized text: {}".format(recognized_text))
        print("Translated text: {}".format(translated_text))
        return recognized_text, translated_text
    else:
        #error_details = result.error_details if result.error_details else "Unknown error"
        print ("Error: {}".format(result.cancellation_details))
        raise Exception("Speech translation failed: {}".format(result.reason))
