import os
import json
import io

def read_scb_file(scb_file_path):
    with open(scb_file_path, 'rb') as file:
        content = file.read()
    return content.split(b'\n')

def read_json_file(json_file_path):
    with io.open(json_file_path, 'r', encoding='utf-8') as file:
        search_terms = json.load(file)
    return [item['message'].encode('cp932') for item in search_terms]

def search_and_extract(scb_lines, search_terms):
    results = []
    for term in search_terms:
        for line in scb_lines:
            if term in line:
                term_index = line.find(term)
                start_byte_index = term_index - 4
                if start_byte_index >= 0:
                    extracted_data = line[start_byte_index:term_index]
                    first_byte = extracted_data[0]
                    first_byte_hex = '0x{:02x}'.format(first_byte)
                else:
                    first_byte_hex = ''
                results.append({
                    'text': term.decode('cp932'),
                    'TL key': term.decode('cp932'),
                    'byte_length': first_byte_hex
                })
                break
        else:
            results.append({
                'text': term.decode('cp932'),
                'TL key': term.decode('cp932'),
                'byte_length': None
            })
    return results

def write_results_to_json(results, output_file_path):
    with io.open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(results, file, indent=4, ensure_ascii=False)

def process_files(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith('.scb'):
            scb_file_path = os.path.join(input_folder, filename)
            json_file_path = os.path.join(input_folder, f"{os.path.splitext(filename)[0]}.scb.json")
            output_file_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.off.json")
            scb_lines = read_scb_file(scb_file_path)
            search_terms = read_json_file(json_file_path)
            results = search_and_extract(scb_lines, search_terms)
            write_results_to_json(results, output_file_path)

if __name__ == "__main__":
    input_folder = 'input_folder'
    output_folder = 'output_folder'
    process_files(input_folder, output_folder)
