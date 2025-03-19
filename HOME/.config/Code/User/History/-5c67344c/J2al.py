import os
import time
import threading
import queue
import azure.cognitiveservices.speech as speechsdk
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.text import TextTranslationClient

# def translate_audio_file(audio_file_path, target_language, speech_key, speech_region, source_language="en-US"):
#     # Create a translation configuration using your subscription info
#     translation_config = speechsdk.translation.SpeechTranslationConfig(
#         subscription=speech_key, region=speech_region)

#     #Set the source language for recognition
#     translation_config.speech_recognition_language = source_language
    
#     # Add the target language for translation
#     translation_config.add_target_language(target_language)
    
#     # Specify the audio input from a file
#     audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
    
#     # Create the TranslationRecognizer with the given config and audio input
#     recognizer = speechsdk.translation.TranslationRecognizer(
#         translation_config=translation_config,
#         audio_config=audio_config)
    
#     # Perform the recognition and translation (synchronously)
#     result = recognizer.recognize_once_async().get()
    
#     # Check the result and return the translated text
#     if result.reason == speechsdk.ResultReason.TranslatedSpeech:
#         recognized_text = result.text
#         translated_text = result.translations[target_language]
#         print("Recognized text: {}".format(recognized_text))
#         print("Translated text: {}".format(translated_text))
#         return recognized_text, translated_text
#     else:
#         #error_details = result.error_details if result.error_details else "Unknown error"
#         print ("Error: {}".format(result.cancellation_details))
#         raise Exception("Speech translation failed: {}".format(result.reason))

def translate_audio_file(audio_file_path, target_language, speech_key, speech_region, source_language="en-US", recognised_text_queue=None, translated_text_queue=None):
    """
    Translates the entire audio file into text and translates it into the target language using
    Azure Speech Translation continuous recognition.

    Parameters:
        audio_file_path (str): Path to the input audio file.
        target_language (str): BCP-47 language tag for the target translation language (e.g., "fr").
        speech_key (str): Azure Speech service subscription key.
        speech_region (str): Azure region (e.g., "westus").
        source_language (str): BCP-47 language tag for the source language (default "en-US").

    Returns:
        tuple: (full_recognized_text, full_translated_text)
    """
    # Create translation configuration and set languages
    translation_config = speechsdk.translation.SpeechTranslationConfig(
        subscription=speech_key, region=speech_region)
    translation_config.speech_recognition_language = source_language
    translation_config.add_target_language(target_language)

    # Specify audio input from file
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)

    # Create the TranslationRecognizer for continuous recognition
    recognizer = speechsdk.translation.TranslationRecognizer(
        translation_config=translation_config, audio_config=audio_config)

    
    is_recognised_queue = False
    is_translated_queue = False

    if recognised_text_queue is None:
        is_recognised_queue = True
    if translated_text_queue is None:
        is_translated_queue = True

    print(f"Recognised queue: {is_recognised_queue}")
    print(f"Translated queue: {is_translated_queue}")

    # Variables to accumulate results
    recognized_segments = []
    translated_segments = []

    # Event to signal when recognition is done
    done_event = threading.Event()

    def recognized_cb(evt):
        # This callback is invoked for each final recognition result
        if evt.result.reason == speechsdk.ResultReason.TranslatedSpeech:
            recognized_segments.append(evt.result.text)
            translated_segments.append(evt.result.translations[target_language])
            if is_recognised_queue:
                recognised_text_queue.put(evt.result.text)
            if is_translated_queue: 
                translated_text_queue.put(evt.result.translations[target_language])
            print("[Segment recognized]: {}".format(evt.result.text))
            print("[Segment translated]: {}\n".format(evt.result.translations[target_language]))

    def session_stopped_cb(evt):
        # Called when the session ends; signal completion.
        print("[Session stopped]: {}\n".format(evt))
        done_event.set()

    def canceled_cb(evt):
        # Called if recognition is canceled; signal completion.
        print("[Recognition canceled]: {}\n".format(evt))
        done_event.set()

    # Connect the callbacks
    recognizer.recognized.connect(recognized_cb)
    recognizer.session_stopped.connect(session_stopped_cb)
    recognizer.canceled.connect(canceled_cb)

    # Start continuous recognition
    recognizer.start_continuous_recognition_async().get()
    
    # Wait until the recognition session stops (i.e. the file is fully processed)
    done_event.wait()
    
    # Stop the recognizer (if not already stopped)
    recognizer.stop_continuous_recognition_async().get()
    
    # Combine all recognized segments into a full transcript
    full_recognized_text = " ".join(recognized_segments)
    full_translated_text = " ".join(translated_segments)
    
    print("[Full recognized text]: {}\n".format(full_recognized_text))
    print("[Full translated text]: {}\n".format(full_translated_text))
    
    return full_recognized_text, full_translated_text
