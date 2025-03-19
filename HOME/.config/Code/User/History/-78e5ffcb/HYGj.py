
speech_key = "7fJr88MVZklBSl3vDoF7xkKxYtD9vrDYnXALYsoVbT6IG7b4F1NTJQQJ99BAAC5RqLJXJ3w3AAAYACOG0pi9"
service_region = "westeurope"
translator_key = "3iJ3P9yL1KJHkJKHFfQoq7zw2fr3PoH8LLYqd6y78bHSiNW4koxFJQQJ99BAAC5RqLJXJ3w3AAAbACOG807F"
translator_region = "westeurope"
translator_endpoint = "https://api.cognitive.microsofttranslator.com"

import os
import time
import threading
import queue
import azure.cognitiveservices.speech as speechsdk
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.text import TextTranslationClient

# ---------------------- Helper Interfaces ----------------------

def make_output_dir(input_path):
    """
    Creates an output file path by replacing "Original-Audio" with "Translated-Audio"
    and appending "-Translated.wav" to the input filename.
    """
    input_dir = os.path.dirname(input_path)
    input_file_name = os.path.basename(input_path)
    output_dir = input_dir.replace("Original-Audio", "Translated-Audio")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    base_output_path = os.path.join(output_dir, input_file_name.replace(".wav", "-Translated"))
    return base_output_path

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

# ---------------------- Core Pipeline Functions ----------------------

def transcribe_audio_to_queue(file_path, segment_queue, speech_config):
    """
    Sets up continuous recognition on the given file.
    Recognized segments are put into segment_queue as (text, detected_language) tuples.
    When the session ends, a None is enqueued as a sentinel.
    """
    # Auto-detect languages (limit: 4 languages)
    auto_detect_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
        languages=["en-US", "sr-RS", "fr-FR", "it-IT"]
    )
    audio_config = speechsdk.audio.AudioConfig(filename=file_path)
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        auto_detect_source_language_config=auto_detect_config,
        audio_config=audio_config
    )

    def recognized_callback(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            # Get detected language from the result properties.
            detected_language = evt.result.properties[
                speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult
            ]
            text = evt.result.text
            print(f"[Transcription] Detected '{detected_language}': {text}")
            segment_queue.put((text, detected_language))
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized.")
        elif evt.result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = evt.result.cancellation_details
            print(f"Speech Recognition canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")

    # Use an Event to know when the session has ended.
    done = threading.Event()
    def stop_cb(evt):
        print("Transcription session stopped.")
        done.set()

    recognizer.recognized.connect(recognized_callback)
    recognizer.session_stopped.connect(stop_cb)
    recognizer.canceled.connect(stop_cb)

    recognizer.start_continuous_recognition()
    print("Started transcription...")
    # Wait until recognition ends.
    done.wait()
    recognizer.stop_continuous_recognition()
    print("Transcription complete.")
    # Signal no more segments.
    segment_queue.put(None)

def translate_text(input_text, source_language, target_language):
    """
    Translates input_text from source_language to target_language using Azure Translator.
    """
    if not translator_key or not translator_region:
        raise ValueError("Translator key and region must be set.")
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

def synthesize_voice(input_text, language, output_path, speech_config):
    """
    Synthesizes the given input_text using the target language voice.
    """
    if not speech_key or not service_region:
        raise ValueError("Speech key and region must be set.")
    # Set synthesis language and choose voice name.
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
    print(f"Selected voice: {voice}")
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    result = synthesizer.speak_text_async(input_text).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"[Synthesis] Audio written to: {output_path}")
    else:
        print("Speech synthesis failed.")

def pipeline_worker(segment_queue, target_language, base_output_path, speech_config):
    """
    Consumes transcription segments from segment_queue, translates each, and synthesizes to separate audio files.
    """
    segment_index = 0
    while True:
        item = segment_queue.get()
        if item is None:
            segment_queue.task_done()
            break
        transcription_text, detected_language = item
        try:
            print(f"[Pipeline] Translating segment {segment_index}...")
            translated_text = translate_text(
                input_text=transcription_text,
                source_language=detected_language,
                target_language=target_language
            )
            print(f"[Pipeline] Translation for segment {segment_index}: {translated_text}")
            segment_output_path = f"{base_output_path}_segment_{segment_index}.wav"
            print(f"[Pipeline] Synthesizing segment {segment_index} to {segment_output_path}...")
            synthesize_voice(
                input_text=translated_text,
                language=target_language,
                output_path=segment_output_path,
                speech_config=speech_config
            )
        except Exception as e:
            print(f"Error processing segment {segment_index}: {e}")
        finally:
            segment_index += 1
            segment_queue.task_done()

# ---------------------- Main ----------------------

if __name__ == "__main__":
    # Pick the input audio file and target language.
    input_dir = "/home/basic/Projects/Vavilon/Original-Audio"
    audio_file_path = pick_file_interface(input_dir)
    target_language = pick_language_interface()
    base_output_path = make_output_dir(audio_file_path)
    print(f"Input file: {audio_file_path}")
    print(f"Output base path: {base_output_path}\n")

    # Create a global SpeechConfig for both transcription and synthesis.
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    # (Optional: adjust additional properties on speech_config here)

    # Create a thread-safe queue for segments.
    segment_queue = queue.Queue()

    # Start the pipeline worker thread (translation and synthesis).
    worker_thread = threading.Thread(target=pipeline_worker,
                                     args=(segment_queue, target_language, base_output_path, speech_config))
    worker_thread.start()

    start_time = time.time()
    # Start transcription in a separate thread so that it runs in parallel.
    transcription_thread = threading.Thread(target=transcribe_audio_to_queue,
                                            args=(audio_file_path, segment_queue, speech_config))
    transcription_thread.start()

    # Wait for transcription and pipeline processing to complete.
    transcription_thread.join()
    segment_queue.join()
    worker_thread.join()
    end_time = time.time()

    print("Pipeline processing complete.")
    print(f"Total time elapsed: {end_time - start_time:.2f} seconds")
