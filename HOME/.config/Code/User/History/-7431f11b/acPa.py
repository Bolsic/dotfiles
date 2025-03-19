import os
import time
import threading
import queue
from pydub import AudioSegment  # pip install pydub

import azure.cognitiveservices.speech as speechsdk
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.text import TextTranslationClient

speech_key = "7fJr88MVZklBSl3vDoF7xkKxYtD9vrDYnXALYsoVbT6IG7b4F1NTJQQJ99BAAC5RqLJXJ3w3AAAYACOG0pi9"
service_region = "westeurope"
translator_key = "3iJ3P9yL1KJHkJKHFfQoq7zw2fr3PoH8LLYqd6y78bHSiNW4koxFJQQJ99BAAC5RqLJXJ3w3AAAbACOG807F"
translator_region = "westeurope"
translator_endpoint = "https://api.cognitive.microsofttranslator.com"

# (Assume that speech_key, service_region, translator_key, translator_region are set)

def make_output_dir(input_path):
    # The output directory is ...Translated-Audio with the input filename modified.
    input_dir = os.path.dirname(input_path)
    input_file_name = os.path.basename(input_path)
    output_dir = input_dir.replace("Original-Audio", "Translated-Audio")
    base_output_path = os.path.join(output_dir, input_file_name.replace(".wav", "-Translated"))
    return base_output_path

# Global list to store temporary segment file paths (maintaining order)
synthesized_segments = []

def transcribe_audio_to_queue(file_path, segment_queue):
    """
    Sets up continuous recognition. Each recognized phrase (with its detected language)
    is placed into the segment_queue immediately.
    """
    if not speech_key or not service_region:
        print("Environment variables for Azure Speech service are not set.")
        return

    # Auto-detect languages (up to 4)
    auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
        languages=["en-US", "sr-RS", "fr-FR", "it-IT"]
    )

    # Set up the audio configuration
    audio_config = speechsdk.audio.AudioConfig(filename=file_path)

    # Create a speech recognizer
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speechsdk.SpeechConfig(subscription=speech_key, region=service_region),
        auto_detect_source_language_config=auto_detect_source_language_config,
        audio_config=audio_config
    )

    def recognized_callback(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            # Retrieve the detected language from the result properties
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

    # Connect the callback to the recognized event
    recognizer.recognized.connect(recognized_callback)

    # Use an event to wait until the session is over
    done = threading.Event()

    def stop_cb(evt):
        done.set()

    recognizer.session_stopped.connect(stop_cb)
    recognizer.canceled.connect(stop_cb)

    recognizer.start_continuous_recognition()
    print("Started transcription...")

    # Wait until the session is done.
    done.wait()

    recognizer.stop_continuous_recognition()
    print("Transcription complete.")

    # Signal to the consumer that no more segments will be coming.
    segment_queue.put(None)

def translate_text(input_text, source_language, target_language):
    if not translator_key or not translator_region:
        raise ValueError("Azure Translator service key and region must be set as environment variables.")

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
        raise ValueError("Azure Speech service key and region must be set as environment variables.")

    # Create a synthesis configuration for this operation
    synthesis_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    synthesis_config.speech_synthesis_language = language

    # Choose a voice based on the language
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

    synthesis_config.speech_synthesis_voice_name = voice
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)

    synthesizer = speechsdk.SpeechSynthesizer(speech_config=synthesis_config, audio_config=audio_config)
    result = synthesizer.speak_text_async(input_text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"[Synthesis] Audio written to: {output_path}")
    else:
        print("Speech synthesis canceled or failed.")

def pipeline_worker(segment_queue, target_language, base_output_path):
    """
    Worker thread: continuously pulls segments from the queue, translates, and synthesizes them.
    Each segment is saved to a temporary file and its path is stored in a global list.
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

            # Create a temporary output file name for this segment
            segment_output_path = f"{base_output_path}_segment_{segment_index}.wav"
            print(f"[Pipeline] Synthesizing segment {segment_index} to {segment_output_path}...")
            synthesize_voice(
                input_text=translated_text,
                language=target_language,
                output_path=segment_output_path
            )
            # Store the segment file path for later concatenation
            synthesized_segments.append(segment_output_path)
        except Exception as e:
            print(f"Error processing segment {segment_index}: {e}")
        finally:
            segment_index += 1
            segment_queue.task_done()

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

    base_output_path = make_output_dir(audio_file_path)
    print(f"Input path: {audio_file_path}")
    print(f"Base output path (for segments): {base_output_path}\n\n")

    return audio_file_path, base_output_path

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
            print(f"You have selected: {selected_language}\n\n")
        else:
            print("Invalid selection. Please run the program again and choose a valid number.")
            exit(1)
    except ValueError:
        print("Invalid input. Please enter a number corresponding to the language.")
        exit(1)

    return selected_language

if __name__ == "__main__":
    # Define the directory for the input audio file.
    directory_path = "/home/basic/Projects/Vavilon/Original-Audio"
    audio_file_path, base_output_path = pick_file_interface(directory_path)

    # Select the target language for translation/synthesis.
    target_language = pick_language_interface()

    # Create a thread-safe queue for segments.
    segment_queue = queue.Queue()

    # Create and start the pipeline worker thread.
    worker_thread = threading.Thread(target=pipeline_worker, args=(segment_queue, target_language, base_output_path))
    worker_thread.start()

    # Start transcription (can be in the main thread or its own thread)
    start_time = time.time()
    transcribe_audio_to_queue(audio_file_path, segment_queue)

    # Wait for all queued segments to be processed.
    segment_queue.join()
    worker_thread.join()

    # --- Concatenate synthesized segments into one final audio file ---
    final_output_path = base_output_path + ".wav"
    print("Concatenating segments into final output file:", final_output_path)

    if synthesized_segments:
        combined = AudioSegment.empty()
        # Assuming segments are processed in order; otherwise, sort by segment index
        for seg_file in synthesized_segments:
            segment_audio = AudioSegment.from_file(seg_file)
            combined += segment_audio
        combined.export(final_output_path, format="wav")
        print(f"Final audio file saved to {final_output_path}")
    else:
        print("No segments were synthesized.")

    end_time = time.time()
    print("Pipeline processing complete.")
    print(f"Total time elapsed: {end_time - start_time} seconds")
