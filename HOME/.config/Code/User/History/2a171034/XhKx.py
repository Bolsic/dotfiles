import toml
import os
from systemd import journal


KEY_VALUE_PAIRS_PATH = '/home/basic/DnD/DnD-Notes/Waterdeep/unsorted/keys.toml' 
TARGET_DIRECTORY = '/home/basic/DnD/DnD-Notes/Waterdeep/unsorted'
OBSIDIAN_VAULT_PATH = '/home/basic/DnD/DnD-Notes/Waterdeep'
FILE_EXEPTIONS = ['keys.toml']


def read_markdown_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        markdown_text = file.read()
        return markdown_text


# Tags are syntaxed as "#tag"
def get_tags(text):
    tags = []
    # Reading the first four line only
    for line in text.split('\n')[0:4]:
        for word in line.split(' '):
            if word.startswith('#'):
                # Eliminating the '#' from the word
                word = word[1:]
                # Sorting out heading lines
                if not word.startswith('#'): tags.append(word)
    return tags


# Reading the .toml file containing the key-value pairs
def read_key_value_pairs(text):
    key_value_pairs = {}
    keys = toml.load(KEY_VALUE_PAIRS_PATH)
    return keys

 
# Calculating the new path for the file
def get_new_path(file_path, obsidian_vault_path=OBSIDIAN_VAULT_PATH):
    file_name = file_path.split('/')[-1]
    text_content = read_markdown_text(file_path)
    tags = get_tags(text_content)
    keys = read_key_value_pairs(KEY_VALUE_PAIRS_PATH)
 
    for tag in tags:

        # Return based on the first tag that matches with the keys
        if tag in keys:
            new_path = os.path.join(obsidian_vault_path, keys[tag], file_path.split('/')[-1])
            journal.write("   Moved file: " + file_name + " ---> " + new_path)
            return new_path
        
    # If no tags are found, move the file to the unsorted folder
    journal.write("   Moved file: " + file_name + " ---> NOT SORTED")
    return None
        


def sort_files(target_directory=TARGET_DIRECTORY, file_exceptions=FILE_EXEPTIONS, keys_path=KEY_VALUE_PAIRS_PATH, obsidian_vault_path=OBSIDIAN_VAULT_PATH):
    
    journal.write("Sorting files in directory: " + target_directory)    
    
    for filename in os.listdir(target_directory):
        if filename not in file_exceptions:
            file_path = os.path.join(target_directory, filename)

            new_path = get_new_path(file_path)

            if new_path:            
                os.rename(file_path, new_path)   

    journal.write("Finished sorting files in directory: " + target_directory)


sort_files()