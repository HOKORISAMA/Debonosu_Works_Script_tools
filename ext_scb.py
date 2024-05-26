# -*- coding: shift-jis -*-

import os
import json
import re

def is_japanese(text):
    # Regular expression to match Japanese characters
    japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\uF900-\uFAFF]+')
    return bool(japanese_pattern.search(text))

def contains_half_width_kana(text):
    # Regular expression to match half-width hiragana and katakana characters
    half_width_kana_pattern = re.compile(r'[\uff61-\uff9f]+')
    return bool(half_width_kana_pattern.search(text))
    
def contains_control_characters(text):
    # Regular expression to match control characters like \u0003, \u0004, \u0007
    control_character_pattern = re.compile(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]+')
    return bool(control_character_pattern.search(text))

def contains_byte_80(text):
    return b'\x80' in text.encode('cp932', errors='ignore')

def filter_special_characters(text):
    # Regular expression to remove special characters like '*', '@'
    special_character_pattern = re.compile(r'[*@]')
    return special_character_pattern.sub('', text)

def filter_single_letter_lines(data):
    filtered_data = [entry for entry in data if len(entry['text']) > 1]
    return filtered_data

def filter_half_width_english_lines(data):
    filtered_data = [entry for entry in data if not re.match(r'^[A-Za-z][^\u3000-\u303F\uFF00-\uFFEF\s]+$', entry['text'])]
    return filtered_data


def filter_japanese_lines(data):
    japanese_data = [entry for entry in data if is_japanese(entry['text']) 
                     and not contains_control_characters(entry['text']) 
                     and not contains_byte_80(entry['text'])
                     and not contains_half_width_kana(entry['text'])]
    return japanese_data

def read_scb_file(file_path):
    scb_data = []
    with open(file_path, 'rb') as file:
        while True:
            line = file.readline()
            if not line:
                break
            text_parts = line.split(b'\x00')  # Split the line at each null byte
            for text_part in text_parts:
                text = text_part.decode('cp932', errors='ignore').strip()  # Decode using CP932 encoding, ignoring errors
                text = filter_special_characters(text)  # Remove special characters
                if text:
                    byte_length = hex(len(text_part) + 1)  # Add 1 to byte length before converting to hex
                    scb_entry = {
                        "text": text,
                        "TL key": text,
                        "byte_length": byte_length
                    }
                    scb_data.append(scb_entry)
    return scb_data

def process_folder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".scb"):
            input_file_path = os.path.join(input_folder, filename)
            output_file_path = os.path.join(output_folder, f"{filename.split('.')[0]}.json")

            scb_data = read_scb_file(input_file_path)
            filtered_data = filter_japanese_lines(scb_data)
            filtered_data = filter_single_letter_lines(filtered_data)
            filtered_data = filter_half_width_english_lines(filtered_data)

            for entry in filtered_data:
                entry["byte_length"] = "0x{:02X}".format(int(entry["byte_length"], 16))

            with open(output_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(filtered_data, json_file, indent=4, ensure_ascii=False)

            print(f"Filtered data from {filename} saved to: {output_file_path}")


def main():
    input_folder = "input_scb_files"  # Change this to the path of your folder containing .scb files
    output_folder = "translatable_files"  # Change this to the path of the output folder
    process_folder(input_folder, output_folder)

if __name__ == "__main__":
    main()
