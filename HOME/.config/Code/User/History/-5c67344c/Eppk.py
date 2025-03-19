import os
import time
import threading
import queue
import azure.cognitiveservices.speech as speechsdk
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.text import TextTranslationClient

def translate_audio_file(audio_file_path, target_language, speech_key, speech_region, source_language="en-US", recognised_text_queue=None, translated_text_queue=None, done_event=None):

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

    
    is_recognised_queue = True
    is_translated_queue = True

    if recognised_text_queue is None:
        is_recognised_queue = False
    if translated_text_queue is None:
        is_translated_queue = False

    print(f"Recognised queue: {is_recognised_queue}")
    print(f"Translated queue: {is_translated_queue}")

    # Variables to accumulate results
    recognized_segments = []
    translated_segments = []

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


def translate_live_audio(speech_key, speech_region, source_language, target_language,
                         recognized_text_queue, translated_text_queue, stop_event, done_event):
    """
    Performs continuous translation from live microphone audio.
    As segments are recognized, the recognized text and its translation are enqueued.

    Parameters:
        speech_key (str): Azure Speech subscription key.
        speech_region (str): Azure region (e.g., "westus").
        source_language (str): The language spoken by the user (e.g., "en-US").
        target_language (str): The language to translate to (e.g., "fr").
        recognized_text_queue (queue.Queue): Queue to store recognized text.
        translated_text_queue (queue.Queue): Queue to store translated text.
        stop_event (threading.Event): External event to signal stopping.
        done_event (threading.Event): Event to signal that recognition has ended.
    """
    # Set up translation configuration.
    translation_config = speechsdk.translation.SpeechTranslationConfig(
        subscription=speech_key, region=speech_region)
    translation_config.speech_recognition_language = source_language
    translation_config.add_target_language(target_language)

    # Use the default microphone for audio input.
    try:
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    except AttributeError:
        raise AttributeError("AudioConfig.from_default_microphone_input() not found. "
                             "Please upgrade your azure-cognitiveservices-speech package (pip install --upgrade azure-cognitiveservices-speech).")

    # Create a TranslationRecognizer for continuous recognition.
    recognizer = speechsdk.translation.TranslationRecognizer(
        translation_config=translation_config, audio_config=audio_config)

    recognized_segments = []
    translated_segments = []

    def recognized_cb(evt):
        if evt.result.reason == speechsdk.ResultReason.TranslatedSpeech:
            recognized_segments.append(evt.result.text)
            translated = evt.result.translations[target_language]
            translated_segments.append(translated)
            if recognized_text_queue is not None:
                recognized_text_queue.put(evt.result.text)
            if translated_text_queue is not None:
                translated_text_queue.put(translated)
            print(f"[Segment recognized]: {evt.result.text}")
            print(f"[Segment translated]: {translated}\n")

    def session_stopped_cb(evt):
        print(f"[Session stopped]: {evt}\n")
        done_event.set()

    def canceled_cb(evt):
        print(f"[Recognition canceled]: {evt}\n")
        done_event.set()

    # Connect callbacks.
    recognizer.recognized.connect(recognized_cb)
    recognizer.session_stopped.connect(session_stopped_cb)
    recognizer.canceled.connect(canceled_cb)

    # Start continuous recognition.
    recognizer.start_continuous_recognition_async().get()
    print("Live translation started. Speak into your microphone...")

    # Run until stop_event is set.
    while not stop_event.is_set():
        time.sleep(0.5)

    # Stop recognition.
    recognizer.stop_continuous_recognition_async().get()
    full_recognized_text = " ".join(recognized_segments)
    full_translated_text = " ".join(translated_segments)
    print(f"[Full recognized text]: {full_recognized_text}\n")
    print(f"[Full translated text]: {full_translated_text}\n")

    done_event.set()
    return full_recognized_text, full_translated_text
