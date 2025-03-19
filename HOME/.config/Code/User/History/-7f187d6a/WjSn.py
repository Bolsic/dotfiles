import os
import time
import azure.cognitiveservices.speech as speechsdk
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.text import TextTranslationClient

speech_key = "8DWayvEHZerwdy1oXOhSMJRQJ2ic0boQIkoVo6BhVwbHMDGRnLiiJQQJ99BBAC5RqLJXJ3w3AAAYACOGKpnv"
service_region = "westeurope"
translator_key = "8uzkNOPtkQURJWrm2Zxih0R0NpHJ36rXNoVUG9226ZJ2Yx6pMcLSJQQJ99BBAC5RqLJXJ3w3AAAbACOGpome"
translator_region = "westeurope"
translator_endpoint = "https://api.cognitive.microsofttranslator.com"

def make_output_dir(input_path):
    # The output directory is /home/basic/Projects/Vavilon/Translated-Audio + the name of the input directory with "-Translated" appended
    input_dir = os.path.dirname(input_path)
    input_file_name = os.path.basename(input_path)
    output_dir = input_dir.replace("Original-Audio", "Translated-Audio")
    output_path = os.path.join(output_dir, input_file_name.replace(".wav", "-Translated.wav"))

    return output_path



def transcribe_audio(file_path):

    if not speech_key or not service_region:
        print("Environment variables for Azure Speech service are not set.")
        return

    # Set up the speech configuration

    auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
        # Apperently the limit is 4 languages
        languages=[
            "en-US", 
            "sr-RS",
            "fr-FR",
            "it-IT"
        ]
    )

    #speech_config.speech_recognition_language = language

    # Set up the audio configuration
    audio_config = speechsdk.audio.AudioConfig(filename=file_path)

    # Create a speech recognizer
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        auto_detect_source_language_config=auto_detect_source_language_config,
        audio_config=audio_config
    )

    transcriptions = []
    detected_languages = []

    def recognised_callback(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            detected_language = evt.result.properties[
                speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult
            ]
            transcriptions.append(evt.result.text)
            detected_languages.append(detected_language)

            #print(f"Detected Language: {detected_language}")
            #print(f"Transcription: {evt.result.text}")
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized.")
        elif evt.result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = evt.result.cancellation_details
            print(f"Speech Recognition canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")


    # Connect the callback function to the recognized event
    speech_recognizer.recognized.connect(recognised_callback)

    # Start continuous recognition
    speech_recognizer.start_continuous_recognition()

    # Wait until the recognition is complete
    done = False
    def stop_cb(evt):
        nonlocal done
        done = True

    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    while not done:
        pass

    # Stop continuous recognition
    speech_recognizer.stop_continuous_recognition()

    # The detected language is the most often detected language
    detected_language = max(set(detected_languages), key=detected_languages.count)

    # Combine all recognized text segments
    full_transcription = " ".join(transcriptions)

    return full_transcription, detected_language
    

def translate_text(input_text, source_language, target_language):

    if not translator_key or not translator_region:
        raise ValueError("Azure Translator service key and region must be set as environment variables.")

    # Set up the Text Translation client
    credential = AzureKeyCredential(translator_key)
    text_translator = TextTranslationClient(credential=credential, region=translator_region)

    # Perform the translation
    response = text_translator.translate(
        body=[input_text],
        to_language=[target_language],
        from_language=source_language,
        to_script="Latn" if target_language == "sr-RS" else None
    )

    # Extract the translated text from the response
    if response and response[0].translations:
        translated_text = response[0].translations[0].text
        return translated_text
    else:
        raise Exception("Translation failed. No response received.")
    

def synthesize_voice(input_text, language, output_path):
    
    if not speech_key or not service_region:
        raise ValueError("Azure Speech service key and region must be set as environment variables.")

    speech_config.speech_synthesis_language = language

    # Set the voice name
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


    speech_config.speech_synthesis_voice_name = voice
    print(f"Selected voice: {voice}")
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    speech_synthesizer.speak_text_async(input_text).get()


def pick_file_interface(dir):
    files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
    print("Files in the directory:")
    for idx, file in enumerate(files, start=1):
        print(f"{idx}. {file}")

    try:
        choice = int(input("Enter the number of the file you want to use: "))
        if 1 <= choice <= len(files):
            selected_file = files[choice - 1]
            print(f"You have selected: {selected_file}\n")
            audio_file_path = os.path.join(dir, selected_file)
        else:
            print("Invalid selection. Please run the program again and choose a valid number.")
    except ValueError:
        print("Invalid input. Please enter a number corresponding to the file.")

    output_path = make_output_dir(audio_file_path)
    print(f"Input path: {audio_file_path}")
    print(f"Output path: {output_path}\n\n")

    return audio_file_path, output_path


def pick_language_interface():
    print("Select the language of the audio:")
    print("1. English")
    print("2. Serbian")
    print("3. French")
    print("4. German")
    try:
        choice = int(input("Enter the number of the language: "))
        if 1 <= choice <= 4:
            languages = ["en-US", "sr-RS", "fr-FR", "de-DE"]
            selected_language = languages[choice - 1]
            print(f"You have selected: {selected_language}\n\n")
        else:
            print("Invalid selection. Please run the program again and choose a valid number.")
    except ValueError:
        print("Invalid input. Please enter a number corresponding to the language.")

    return selected_language
    


if __name__ == "__main__":

    audio_file_path = "/home/basic/Projects/Vavilon/Original-Audio/Djokic-Intro-English.wav"
    #audio_file_path = "/home/basic/Projects/Vavilon/Original-Audio/test-audio-1.wav"

    directory_path = "/home/basic/Projects/Vavilon/Original-Audio"

    audio_file_path, output_path = pick_file_interface(directory_path)
    
    # Select the language to translate to
    selecred_language = pick_language_interface()

    # Set up the speech configuration
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

    #Measure time elapsed
    start = time.time()

    print("Transcribing audio...")
    transcription, input_language = transcribe_audio(audio_file_path)
    print(f"Detected language: {input_language}")
    print(f"Transcription: \n{transcription}\n\n")

    print("Translating text...")
    translated_text = translate_text(input_text=transcription, source_language=input_language, target_language=selecred_language)
    print(f"Translation: \n{translated_text}\n\n")

    print("Synthesizing voice...")
    synthesize_voice(translated_text, language=selecred_language, output_path=output_path)
    print(f"Output saved to: {output_path}")
    print("Done!")

    end = time.time()

    print(f"Time elapsed: {end - start}")
