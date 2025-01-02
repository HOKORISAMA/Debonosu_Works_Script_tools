import struct
import json
from pathlib import Path
from enum import Enum
import logging
from typing import List, Dict

class Mode(Enum):
    EXTRACT = 'extract'
    REPLACE = 'replace'

class StringTool:
    def __init__(self, encoding='cp932'):
        self.encoding = encoding
        self.logger = logging.getLogger(__name__)
        
        # Define fixed directories
        self.input_dir = Path('input_files')
        self.json_dir = Path('json_files')
        self.output_dir = Path('output_files')
        
        # Create directories if they don't exist
        self.json_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
    def _find_string_pattern(self, data: bytes, pos: int) -> tuple[bool, int, int, int]:
        """
        Find the next valid string pattern in binary data.
        Returns (is_valid, string_length, string_start, string_end)
        """
        if (pos + 5 >= len(data) or 
            data[pos] != 0x04 or 
            data[pos + 2:pos + 5] != b'\x00\x00\x00'):
            return False, 0, 0, 0
            
        specified_length = data[pos + 1]
        str_start = pos + 5
        str_end = str_start
        
        while str_end < len(data) and data[str_end] != 0:
            str_end += 1
            
        actual_length = str_end - str_start + 1
        if actual_length != specified_length:
            return False, 0, 0, 0
            
        return True, specified_length, str_start, str_end

    def extract_strings(self, binary_file_path: Path) -> List[Dict[str, str]]:
        """Extract strings from binary file."""
        extracted_strings = []
        
        with open(binary_file_path, 'rb') as f:
            data = f.read()
        
        pos = 0
        while pos < len(data):
            is_valid, length, str_start, str_end = self._find_string_pattern(data, pos)
            
            if is_valid:
                try:
                    original_str = data[str_start:str_end].decode(self.encoding)
                    extracted_strings.append({
                        'orig': original_str,
                        'trans': original_str
                    })
                    pos = str_end + 1
                    continue
                except UnicodeDecodeError:
                    self.logger.warning(f"Failed to decode string at position {str_start}")
                    
            pos += 1
            
        return extracted_strings

    def replace_strings(self, binary_file_path: Path, translations: List[Dict[str, str]], 
                       output_file_path: Path) -> None:
        """
        Replace strings in binary file with translations, maintaining original order.
        Only replaces each string once in the order they appear in the translations list.
        """
        with open(binary_file_path, 'rb') as f:
            data = bytearray(f.read())
        
        pos = 0
        trans_index = 0  # Keep track of which translation we're currently looking for
        
        while pos < len(data) and trans_index < len(translations):
            is_valid, orig_length, str_start, str_end = self._find_string_pattern(data, pos)
            
            if is_valid:
                try:
                    orig_str = data[str_start:str_end].decode(self.encoding)
                    
                    # Only check against the current translation in sequence
                    trans_entry = translations[trans_index]
                    if trans_entry['orig'] == orig_str:
                        new_str = trans_entry['trans'].encode(self.encoding)
                        new_length = len(new_str) + 1
                        
                        data[pos + 1] = new_length
                        data[str_start:str_end] = new_str
                        pos = str_start + new_length
                        trans_index += 1  # Move to next translation
                        continue
                    
                except UnicodeDecodeError:
                    self.logger.warning(f"Failed to decode/encode string at position {str_start}")
            
            pos += 1
        
        if trans_index < len(translations):
            self.logger.warning(f"Not all translations were applied. {len(translations) - trans_index} translations remaining.")
        
        with open(output_file_path, 'wb') as f:
            f.write(data)

    def process_files(self, mode: Mode) -> None:
        """Process all files according to specified mode."""
        if mode == Mode.EXTRACT:
            for file_path in self.input_dir.glob('**/*.scb'):
                try:
                    strings = self.extract_strings(file_path)
                    if strings:
                        json_path = self.json_dir / f"{file_path.stem}.json"
                        with open(json_path, 'w', encoding='utf-8') as f:
                            json.dump(strings, f, indent=4, ensure_ascii=False)
                        self.logger.info(f"Processed {file_path.name}: {len(strings)} strings found")
                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {e}")
                    
        elif mode == Mode.REPLACE:
            for json_path in self.json_dir.glob('*.json'):
                try:
                    binary_path = self.input_dir / f"{json_path.stem}.scb"
                    if binary_path.exists():
                        with open(json_path, 'r', encoding='utf-8') as f:
                            translations = json.load(f)
                        
                        output_file = self.output_dir / binary_path.name
                        self.replace_strings(binary_path, translations, output_file)
                        self.logger.info(f"Applied translations to {binary_path.name}")
                    else:
                        self.logger.warning(f"No matching binary file found for {json_path.stem}")
                except Exception as e:
                    self.logger.error(f"Error processing {json_path}: {e}")

def main():
    logging.basicConfig(level=logging.INFO)
    
    print("Select mode:")
    print("1. Extract strings")
    print("2. Replace strings")
    
    while True:
        choice = input("Enter choice (1 or 2): ").strip()
        if choice == '1':
            mode = Mode.EXTRACT
            break
        elif choice == '2':
            mode = Mode.REPLACE
            break
        print("Invalid choice. Please enter 1 or 2.")
    
    tool = StringTool()
    try:
        tool.process_files(mode)
        print("Processing complete!")
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == '__main__':
    main()
