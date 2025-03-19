import os
import azure.cognitiveservices.speech as speechsdk

def print_translation_result(recognized_text_queue, translated_text_queue, done_event):
    while not done_event.is_set():
        if not recognized_text_queue.empty():
            print(f"PRINT Recognized: {recognized_text_queue.get()}")
        if not translated_text_queue.empty():
            print(f"PRINT Translated: {translated_text_queue.get()}")


def make_output_dir(input_path):
    # The output directory is /home/basic/Projects/Vavilon/Translated-Audio + the name of the input directory with "-Translated" appended
    input_dir = os.path.dirname(input_path)
    input_file_name = os.path.basename(input_path)
    output_dir = input_dir.replace("Test-Audio", "Test-Output")
    output_path = os.path.join(output_dir, input_file_name.replace(".wav", "-Translated.wav"))

    return output_path

def pick_source_language_interface():
    print("Select the language of the audio:")
    print("1. English")
    print("2. Serbian")
    print("3. French")
    print("4. German")
    print("5. Russian")
    print("6. Turkish")

    try:
        choice = int(input("Enter the number of the language: "))
        if 1 <= choice <= 6:
            languages = ["en-US", "sr-RS", "fr-FR", "de-DE", "ru-RU", "tr-TR"]
            selected_language = languages[choice - 1]
            print(f"You have selected: {selected_language}\n\n")
        else:
            print("Invalid selection. Please run the program again and choose a valid number.")
    except ValueError:
        print("Invalid input. Please enter a number corresponding to the language.")

    return selected_language

def pick_target_language_interface():
    print("Select the language of the audio:")
    print("1. English")
    print("2. Serbian")
    print("3. French")
    print("4. German")
    print("5. Russian")
    print("6. Turkish")
    try:
        choice = int(input("Enter the number of the language: "))
        if 1 <= choice <= 6:
            languages = ["en", "sr-Latn", "fr", "de", "ru", "tr"]
            selected_language = languages[choice - 1]
            print(f"You have selected: {selected_language}\n\n")
        else:
            print("Invalid selection. Please run the program again and choose a valid number.")
    except ValueError:
        print("Invalid input. Please enter a number corresponding to the language.")

    return selected_language

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


def pick_voice_interface(translation_language, speech_key, speech_region):
    """
    Lists available voices for the given translation language and prompts the user
    to select one by number.

    Parameters:
        translation_language (str): BCP-47 language code (e.g., "en-US" or "fr-FR").
        speech_key (str): Azure Speech service subscription key.
        speech_region (str): Azure Speech service region (e.g., "westus").

    Returns:
        str: The name of the selected voice (e.g., "en-US-AriaNeural").
    """
    # Configure the Speech SDK for synthesis, setting the language to filter voices.
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_synthesis_language = translation_language

    # Create a synthesizer without an audio output to fetch the available voices.
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    # Retrieve the list of available voices asynchronously.
    voices_result = synthesizer.get_voices_async().get()
    voices = voices_result.voices

    if not voices:
        print(f"No voices available for language {translation_language}.")
        return None

    print(f"Available voices for language {translation_language}:")
    for idx, voice in enumerate(voices):
        print(f"[{idx}] Name: {voice.name}, Locale: {voice.locale}, Gender: {voice.gender}")

    # Prompt the user until a valid number is entered.
    while True:
        try:
            selection = int(input("Enter the number corresponding to your chosen voice: "))
            if 0 <= selection < len(voices):
                chosen_voice = voices[selection].name
                print(f"You selected: {chosen_voice}")
                return chosen_voice
            else:
                print(f"Invalid selection. Please enter a number between 0 and {len(voices)-1}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
