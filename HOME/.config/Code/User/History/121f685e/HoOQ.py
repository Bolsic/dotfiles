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
    
    # Select the language of the audio
    source_language = pick_source_language_interface()

    # Select the language to translate to
    target_language = pick_target_language_interface()

    # Measure time elapsed
    start = time.time()

    # Translate the file
    print("Translating audio...")
    transcription, translation = translate_audio_file(audio_file_path, target_language, speech_key, speech_region, source_language)
