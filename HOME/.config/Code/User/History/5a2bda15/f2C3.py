import os

def print_translation_result(recognized_text, translated_text):
    print("Recognized text: {}\n".format(recognized_text))
    print("Translated text: {}\n".format(translated_text))

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
            languages = ["en-US", "sr-Latn", "fr-FR", "de-DE", "ru-RU", "tr-TR"]
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
