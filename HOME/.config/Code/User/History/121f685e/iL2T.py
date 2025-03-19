import os
import time
import threading
import queue
import azure.cognitiveservices.speech as speechsdk
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.text import TextTranslationClient

from audio_translator import translate_audio_file
from auxiliary_functions import *

speech_key = os.environ.get('SPEECH_KEY')
speech_region = os.environ.get('SPEECH_REGION')

print("\nSPEECH KEY: " + speech_key)
print("SPEECH REGION: " + speech_region + "\n")

if __name__ == "__main__":

    directory_path = "./Original-Audio"

    audio_file_path, output_path = pick_file_interface(directory_path)
    
    # Select the language to translate to
    selected_language = pick_language_interface()

    # Measure time elapsed
    start = time.time()

    # Translate the file
    print("Translating audio...")
    transcription, translation = translate_audio_file(audio_file_path, selected_language, speech_key, speech_region)
    print(f"Transcription: {transcription}")
    print(f"Translation: {translation}")
    