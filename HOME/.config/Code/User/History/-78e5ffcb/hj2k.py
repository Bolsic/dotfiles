
speech_key = "7fJr88MVZklBSl3vDoF7xkKxYtD9vrDYnXALYsoVbT6IG7b4F1NTJQQJ99BAAC5RqLJXJ3w3AAAYACOG0pi9"
service_region = "westeurope"
translator_key = "3iJ3P9yL1KJHkJKHFfQoq7zw2fr3PoH8LLYqd6y78bHSiNW4koxFJQQJ99BAAC5RqLJXJ3w3AAAbACOG807F"
translator_region = "westeurope"
translator_endpoint = "https://api.cognitive.microsofttranslator.com"

import os
import time
import threading
import queue
import wave
import azure.cognitiveservices.speech as speechsdk
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.text import TextTranslationClient



# ---------------- Helper Functions ----------------

def make_output_dir(input_path):
    """
    Generate the base output path by replacing "Original-Audio" with "Translated-Audio"
    and appending "-Translated" to the filename.
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

def translate_text(input_text, source_language, target_language):
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
        return response[0].translations[0].text
    else:
        raise Exception("Translation failed. No response received.")

def synthesize_voice(input_text, language, output_path, speech_config):
    if not speech_key or not service_region:
        raise ValueError("Speech key and region must be set.")
    speech_config.speech_synthesis_language = language
    # Select voice based on language:
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
    print(f"[Synthesis] Using voice: {voice}")
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    result = synthesizer.speak_text_async(input_text).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"[Synthesis] Audio saved to: {output_path}")
    else:
        print("[Synthesis] Failed to synthesize speech.")

# ------------------ Pipeline Threads ------------------

def push_stream_worker(file_path, push_stream):
    """
    Reads the WAV file in chunks and writes data to the push_stream.
    """
    # Adjust chunk size (in bytes) as needed; 3200 bytes is a common chunk size for 16kHz,16-bit mono
    chunk_size = 3200
    try:
        wf = wave.open(file_path, "rb")
    except Exception as e:
        print(f"Error opening file: {e}")
        push_stream.close()
        return
    try:
        while True:
            data = wf.readframes(chunk_size // 2)
            if not data:
                break
            push_stream.write(data)
            time.sleep(0.1)
    finally:
        wf.close()
        push_stream.close()  # Signal end of stream

def transcribe_audio(push_stream, segment_queue, speech_config):
    """
    Uses a PushAudioInputStream so that the file can be fed in real time.
    Recognized segments are enqueued into segment_queue.
    """
    auto_detect_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
        languages=["en-US", "sr-RS", "fr-FR", "it-IT"]
    )
    audio_config = speechsdk.audio.AudioConfig(stream=push_stream)
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        auto_detect_source_language_config=auto_detect_config,
        audio_config=audio_config
    )

    def recognized_callback(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech and evt.result.text:
            # Get detected language property
            detected_language = evt.result.properties[
                speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult
            ]
            print(f"[Transcription] Detected '{detected_language}': {evt.result.text}")
            segment_queue.put((evt.result.text, detected_language))
        elif evt.result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = evt.result.cancellation_details
            print(f"[Transcription] Canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"[Transcription] Error details: {cancellation_details.error_details}")

    done_event = threading.Event()
    def stop_callback(evt):
        print("[Transcription] Session stopped.")
        done_event.set()

    recognizer.recognized.connect(recognized_callback)
    recognizer.session_stopped.connect(stop_callback)
    recognizer.canceled.connect(stop_callback)

    recognizer.start_continuous_recognition()
    print("[Transcription] Started continuous recognition.")
    done_event.wait()  # Wait until the recognizer stops (i.e. end-of-stream)
    recognizer.stop_continuous_recognition()
    print("[Transcription] Recognition complete.")
    segment_queue.put(None)  # Signal end of segments

def pipeline_worker(segment_queue, target_language, base_output_path, speech_config):
    """
    For each segment in the queue, translates and synthesizes the translated text.
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
            print(f"[Pipeline] Translation {segment_index}: {translated_text}")
            segment_output_path = f"{base_output_path}_segment_{segment_index}.wav"
            print(f"[Pipeline] Synthesizing segment {segment_index} to {segment_output_path}...")
            synthesize_voice(
                input_text=translated_text,
                language=target_language,
                output_path=segment_output_path,
                speech_config=speech_config
            )
        except Exception as e:
            print(f"[Pipeline] Error processing segment {segment_index}: {e}")
        finally:
            segment_index += 1
            segment_queue.task_done()

# ------------------ Main ------------------

if __name__ == "__main__":
    # Pick input file and target language.
    input_dir = "/home/basic/Projects/Vavilon/Original-Audio"
    audio_file_path = pick_file_interface(input_dir)
    target_language = pick_language_interface()
    base_output_path = make_output_dir(audio_file_path)
    print(f"Input file: {audio_file_path}")
    print(f"Output base path: {base_output_path}\n")

    # Create a global SpeechConfig instance.
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    # (Optionally, set additional properties on speech_config here.)

    # Create a thread-safe queue for transcription segments.
    segment_queue = queue.Queue()

    # Create a push stream to feed audio in real time.
    push_stream = speechsdk.audio.PushAudioInputStream()

    # Start a thread that will read the audio file in chunks and write to the push stream.
    push_thread = threading.Thread(target=push_stream_worker, args=(audio_file_path, push_stream))
    push_thread.start()

    # Start the transcription thread that reads from the push stream.
    transcription_thread = threading.Thread(target=transcribe_audio, args=(push_stream, segment_queue, speech_config))
    transcription_thread.start()

    # Start the pipeline worker thread (translation and synthesis).
    worker_thread = threading.Thread(target=pipeline_worker, args=(segment_queue, target_language, base_output_path, speech_config))
    worker_thread.start()

    # Wait for all threads to complete.
    push_thread.join()
    transcription_thread.join()
    segment_queue.join()  # Wait until all segments are processed.
    worker_thread.join()

    print("Pipeline processing complete.")
