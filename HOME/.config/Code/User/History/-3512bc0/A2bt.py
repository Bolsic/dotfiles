import os
import time
import threading
import queue

import azure.cognitiveservices.speech as speechsdk
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.text import TextTranslationClient
import simpleaudio as sa



speech_key = "7fJr88MVZklBSl3vDoF7xkKxYtD9vrDYnXALYsoVbT6IG7b4F1NTJQQJ99BAAC5RqLJXJ3w3AAAYACOG0pi9"
service_region = "westeurope"
translator_key = "3iJ3P9yL1KJHkJKHFfQoq7zw2fr3PoH8LLYqd6y78bHSiNW4koxFJQQJ99BAAC5RqLJXJ3w3AAAbACOG807F"
translator_region = "westeurope"
translator_endpoint = "https://api.cognitive.microsofttranslator.com"

# (Assume that speech_key, service_region, translator_key, translator_region are set)

def make_output_dir(input_path):
    # The output directory is ...Translated-Audio, with the input filename modified.
    input_dir = os.path.dirname(input_path)
    input_file_name = os.path.basename(input_path)
    output_dir = input_dir.replace("Original-Audio", "Translated-Audio")
    base_output_path = os.path.join(output_dir, input_file_name.replace(".wav", "-Translated"))
    return base_output_path

# (Assume that these keys and regions are defined elsewhere or set as environment variables)
# speech_key, service_region, translator_key, translator_region

def transcribe_audio_to_queue(file_path, segment_queue):
    """
    Sets up continuous recognition. For every recognized phrase,
    its text and detected language are pushed into the segment_queue.
    """
    if not speech_key or not service_region:
        print("Environment variables for Azure Speech service are not set.")
        return
    

    # Configure auto-detection for up to 4 languages.
    auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
        languages=["en-US", "sr-RS", "fr-FR", "it-IT"]
    )

    audio_config = speechsdk.audio.AudioConfig(filename=file_path)

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        auto_detect_source_language_config=auto_detect_source_language_config,
        audio_config=audio_config
    )

    def recognized_callback(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            detected_language = evt.result.properties[
                speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult
            ]
            text = evt.result.text
            print(f"[Transcription] Detected '{detected_language}': {text}")
            # Push the recognized segment into the queue
            segment_queue.put((text, detected_language))
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized.")
        elif evt.result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = evt.result.cancellation_details
            print(f"Speech Recognition canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")

    recognizer.recognized.connect(recognized_callback)

    # Use an event to wait until the recognition session ends.
    done = threading.Event()

    def stop_cb(evt):
        done.set()

    recognizer.session_stopped.connect(stop_cb)
    recognizer.canceled.connect(stop_cb)

    recognizer.start_continuous_recognition()
    print("Started transcription...")

    done.wait()  # Wait until the session is done.

    recognizer.stop_continuous_recognition()
    print("Transcription complete.")

    # Signal that no more segments will be coming.
    segment_queue.put(None)

def translate_text(input_text, source_language, target_language):
    if not translator_key or not translator_region:
        raise ValueError("Azure Translator service key and region must be set as environment variables.")

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

def synthesize_voice(input_text, language, audio_queue):
    """
    Synthesizes the given input_text into speech and puts the resulting audio bytes into audio_queue.
    """
    if not speech_key or not service_region:
        raise ValueError("Azure Speech service key and region must be set as environment variables.")

    # Set the synthesis language and choose a voice.
    speech_config.speech_synthesis_language = language
    match language:
        case "en-US":
            voice = "en-US-AriaNeural"
        case "sr-RS":
            voice = "sr-Latn-RS-NicholasNeural"
        case "fr-FR":
            voice = "fr-FR-DeniseNeural"
        case "de-DE":
            voice = "de-DE-KatjaNeural"
        case _:
            print("Invalid language. Please select a valid language.")
            return

    speech_config.speech_synthesis_voice_name = voice

    # Use a pull stream so we can get the audio data instead of auto-playing it.
    audio_stream = speechsdk.audio.PullAudioOutputStream()
    audio_config = speechsdk.audio.AudioOutputConfig(stream=audio_stream)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    
    # Synthesize audio (this call returns after synthesis is complete)
    result = synthesizer.speak_text_async(input_text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("[Synthesis] Audio synthesized successfully; queuing for playback.")
        # Put the synthesized audio data onto the audio queue.
        audio_queue.put(result.audio_data)
    else:
        print("Speech synthesis canceled or failed.")


def pipeline_worker(segment_queue, target_language, audio_queue):
    """
    Worker thread that processes each segment:
      - Translates the text.
      - Synthesizes the translated text and puts audio into the audio_queue.
    """
    while True:
        item = segment_queue.get()
        if item is None:
            segment_queue.task_done()
            break  # No more segments to process.

        transcription_text, detected_language = item
        try:
            print("[Pipeline] Translating segment...")
            translated_text = translate_text(
                input_text=transcription_text,
                source_language=detected_language,
                target_language=target_language
            )
            print(f"[Pipeline] Translation: {translated_text}")
            print("[Pipeline] Synthesizing audio...")
            synthesize_voice(translated_text, target_language, audio_queue)
        except Exception as e:
            print(f"Error processing segment: {e}")
        finally:
            segment_queue.task_done()


def playback_worker(audio_queue):
    while True:
        audio_bytes = audio_queue.get()
        if audio_bytes is None:
            # Sentinel received: exit the thread.
            audio_queue.task_done()
            break
        # Assuming the audio is 16-bit PCM, mono at 16 kHz (adjust these parameters if needed)
        play_obj = sa.play_buffer(audio_bytes, num_channels=1, bytes_per_sample=2, sample_rate=16000)
        play_obj.wait_done()
        audio_queue.task_done()

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
        else:
            print("Invalid selection. Please run the program again and choose a valid number.")
            exit(1)
    except ValueError:
        print("Invalid input. Please enter a number corresponding to the file.")
        exit(1)

    print(f"Input path: {audio_file_path}\n")
    return audio_file_path

def pick_language_interface():
    print("Select the target language for translation:")
    print("1. English (en-US)")
    print("2. Serbian (sr-RS)")
    print("3. French (fr-FR)")
    print("4. German (de-DE)")
    try:
        choice = int(input("Enter the number of the language: "))
        if 1 <= choice <= 4:
            languages = ["en-US", "sr-RS", "fr-FR", "de-DE"]
            selected_language = languages[choice - 1]
            print(f"You have selected: {selected_language}\n")
        else:
            print("Invalid selection. Please run the program again and choose a valid number.")
            exit(1)
    except ValueError:
        print("Invalid input. Please enter a number corresponding to the language.")
        exit(1)

    return selected_language
if __name__ == "__main__":
    directory_path = "/home/basic/Projects/Vavilon/Original-Audio"
    audio_file_path = pick_file_interface(directory_path)
    target_language = pick_language_interface()

    # Set up speech and translator configurations.
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    credential = AzureKeyCredential(translator_key)
    text_translator = TextTranslationClient(credential=credential, region=translator_region)
    
    # Create thread-safe queues for segments and audio.
    segment_queue = queue.Queue()
    audio_queue = queue.Queue()

    # Start the pipeline worker thread (for translation & synthesis).
    worker_thread = threading.Thread(target=pipeline_worker, args=(segment_queue, target_language, audio_queue))
    worker_thread.start()

    # Start the dedicated audio playback thread.
    playback_thread = threading.Thread(target=playback_worker, args=(audio_queue,))
    playback_thread.start()

    start_time = time.time()

    # Begin transcription; segments will be pushed into the segment_queue.
    transcribe_audio_to_queue(audio_file_path, segment_queue)

    # Wait for all segments to be processed.
    segment_queue.join()
    worker_thread.join()

    # Signal playback worker that no more audio is coming.
    audio_queue.put(None)
    audio_queue.join()
    playback_thread.join()

    end_time = time.time()
    print("Pipeline processing complete.")
    print(f"Total time elapsed: {end_time - start_time} seconds")
