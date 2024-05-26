import os
import json
import io

def update_byte_length(json_file):
    """
    Update the byte length of each entry in the JSON file using Shift-JIS encoding.
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        text = item["TL key"]
        byte_length = len(text.encode('932')) + 1  # Calculate byte length using cp-932 encoding
        byte_length_hex = '0x{:02X}'.format(byte_length)  # Convert to hex with leading zeros
        item["byte_length"] = byte_length_hex  # Update byte length in dictionary

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def read_scb_file(filename):
    """
    Read the contents of an SCB file.
    """
    with open(filename, 'rb') as file:
        return file.read()

def find_and_replace_value(scb_data, json_data):
    """
    Find and replace text in SCB data based on JSON data.
    """
    replaced_indices = set()  # Store indices where replacements are made

    for item in json_data:
        text = item['text'].encode('cp932', errors='ignore')
        tl_key = item['TL key'].encode('cp932', errors='ignore')
        byte_length = int(item['byte_length'], 16)

        scb_stream = io.BytesIO(scb_data)
        scb_stream.seek(0)

        padded_text = b'\x00' + text + b'\x00'  # Pad 00 byte before and after the text
        padded_tl_key = b'\x00' + tl_key + b'\x00'  # Pad 00 byte before and after the TL key

        index = scb_stream.read().find(padded_text)
        while index != -1:
            if index not in replaced_indices:  # Check if this index has not been replaced before
                replaced_indices.add(index)  # Add index to replaced_indices set
                scb_data = scb_data[:index] + scb_data[index + len(padded_text):]

                new_index = index - 3  # Decrement by one byte
                scb_data = scb_data[:new_index] + byte_length.to_bytes(1, 'little') + scb_data[new_index + 1:]

                scb_data = scb_data[:index] + padded_tl_key + scb_data[index:]

                # Find next occurrence of the same text
                index = scb_data.find(padded_text, index + len(padded_tl_key))
            else:
                # If this index has been replaced before, find next occurrence of the text
                index = scb_data.find(padded_text, index + len(padded_tl_key))


    return scb_data

def process_folder(input_folder, json_folder, output_folder):
    """
    Process all SCB files in the input folder, updating their content based on corresponding JSON files from the JSON folder.
    """
    for filename in os.listdir(input_folder):
        if filename.endswith('.scb'):
            scb_filename = os.path.join(input_folder, filename)
            output_filename = os.path.join(output_folder, filename)
            json_filename = os.path.join(json_folder, f"{os.path.splitext(filename)[0]}.json")

            scb_data = read_scb_file(scb_filename)

            with open(json_filename, encoding='utf-8', errors='ignore') as json_file:
                json_data = json.load(json_file)

            scb_data = find_and_replace_value(scb_data, json_data)

            with open(output_filename, 'wb') as output_file:
                output_file.write(scb_data)

def main():
    """
    Main function to update byte lengths in JSON files and process SCB files in the specified folder.
    """
    json_folder_path = 'translatable_files'  # Replace with the path to your folder containing JSON files
    scb_folder_path = 'input_scb_files'  # Replace with the path to your folder containing SCB files
    output_folder_path = 'new_scb_files'  # Replace with the path to your output folder

    for file_name in os.listdir(json_folder_path):
        if file_name.endswith('.json'):
            file_path = os.path.join(json_folder_path, file_name)
            update_byte_length(file_path)
            print(f"Processed: {file_path}")

    process_folder(scb_folder_path, json_folder_path, output_folder_path)

if __name__ == "__main__":
    main()
