import os
import threading
import time
import azure.cognitiveservices.speech as speechsdk

speech_key = "8DWayvEHZerwdy1oXOhSMJRQJ2ic0boQIkoVo6BhVwbHMDGRnLiiJQQJ99BBAC5RqLJXJ3w3AAAYACOGKpnv"
service_region = "westeurope"
translator_key = "8uzkNOPtkQURJWrm2Zxih0R0NpHJ36rXNoVUG9226ZJ2Yx6pMcLSJQQJ99BBAC5RqLJXJ3w3AAAbACOGpome"
translator_region = "westeurope"
translator_endpoint = "https://api.cognitive.microsofttranslator.com"

# Replace these with your actual subscription key and service region.
speech_key = "YOUR_SPEECH_KEY"
service_region = "YOUR_SERVICE_REGION"

# Create a global event to signal when recognition is complete.
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
    # Set up auto-detect language configuration.
    auto_detect_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
        languages=["en-US", "sr-RS", "fr-FR", "it-IT"]
    )
    audio_config = speechsdk.audio.AudioConfig(filename=file_path)
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        auto_detect_source_language_config=auto_detect_config,
        audio_config=audio_config
    )
    
    # Connect callbacks.
    recognizer.recognized.connect(recognized_callback)
    recognizer.session_stopped.connect(stop_callback)
    recognizer.canceled.connect(stop_callback)

    # Start continuous recognition.
    recognizer.start_continuous_recognition()
    # Wait until done_event is set (by session_stopped or canceled).
    done_event.wait()
    recognizer.stop_continuous_recognition()

def pick_file_interface(directory):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if not files:
        print("No files found in the directory.")
        return None
    print("Files in the directory:")
    for idx, file in enumerate(files, start=1):
        print(f"{idx}. {file}")
    try:
        choice = int(input("Enter the number of the file you want to use: "))
        if 1 <= choice <= len(files):
            selected_file = files[choice - 1]
            print(f"You have selected: {selected_file}")
            return os.path.join(directory, selected_file)
        else:
            print("Invalid selection.")
            return None
    except ValueError:
        print("Invalid input; please enter a number.")
        return None

if __name__ == "__main__":
    # Define the directory path where your audio files are stored.
    directory_path = "/home/basic/Projects/Vavilon/Original-Audio"
    
    file_path = pick_file_interface(directory_path)
    if not file_path:
        print("No valid file selected. Exiting.")
        exit(1)
    
    # Create the speech configuration instance.
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    
    # Start recognition in a separate thread.
    recognition_thread = threading.Thread(target=run_recognition, args=(file_path,))
    recognition_thread.start()
    recognition_thread.join()
    
    print("Speech recognition completed.")
