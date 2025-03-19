import threading
import time
import azure.cognitiveservices.speech as speechsdk

speech_key = "8DWayvEHZerwdy1oXOhSMJRQJ2ic0boQIkoVo6BhVwbHMDGRnLiiJQQJ99BBAC5RqLJXJ3w3AAAYACOGKpnv"
service_region = "westeurope"
translator_key = "8uzkNOPtkQURJWrm2Zxih0R0NpHJ36rXNoVUG9226ZJ2Yx6pMcLSJQQJ99BBAC5RqLJXJ3w3AAAbACOGpome"
translator_region = "westeurope"
translator_endpoint = "https://api.cognitive.microsofttranslator.com"

# Create an event to signal completion
done_event = threading.Event()

def recognized_callback(evt):
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"Recognized: {evt.result.text}")
    elif evt.result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = evt.result.cancellation_details
        print(f"Speech Recognition canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")

def stop_callback(evt):
    print("Session stopped, setting done_event.")
    done_event.set()

def run_recognition(file_path):
    # Set up auto-detect languages (or use a specific language)
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
    # Wait until the stop event is signaled
    done_event.wait()
    recognizer.stop_continuous_recognition()

# In your thread, call run_recognition:
import threading
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
recognition_thread = threading.Thread(target=run_recognition, args=("/home/basic/Projects/Vavilon/Original-Audio/Djokic-Intro-English.wav",))
recognition_thread.start()
# Optionally, join the thread if needed:
recognition_thread.join()

