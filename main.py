import struct
import json
from pathlib import Path
from enum import Enum
import logging
from typing import List, Dict, Tuple

class Mode(Enum):
    EXTRACT = 'extract'
    REPLACE = 'replace'

class StringTool:
    def __init__(self, encoding='cp932'):
        """
        A tool for extracting and replacing strings in .scb binary files,
        based on a known pattern:
         - Byte 0: 0x04
         - Byte 1: length_of_string (including null terminator)
         - Bytes 2..4: \x00\x00\x00
         - Followed by <string_data>\0
        """
        self.encoding = encoding
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Define fixed directories
        self.input_dir = Path('input_files')
        self.json_dir = Path('json_files')
        self.output_dir = Path('output_files')
        
        # Create directories if they don't exist
        self.json_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
    def _find_string_pattern(self, data: bytes, offset: int) -> Tuple[bool, int, int, int]:
        """
        Find the next valid string pattern in binary data at 'offset'.
        Returns (is_valid, string_length, string_start, string_end).
        
        * is_valid: boolean indicating if a valid pattern is found
        * string_length: the length byte stored in data[offset+1], i.e. expected length
        * string_start: index in 'data' where the string itself starts
        * string_end: index in 'data' where the null terminator was found (excluded from substring)
        """
        # Ensure we don't read past end
        if offset + 5 >= len(data):
            return False, 0, 0, 0
        
        # Check pattern 0x04, 0x00 0x00 0x00 at right positions
        if data[offset] != 0x04 or data[offset+2:offset+5] != b'\x00\x00\x00':
            return False, 0, 0, 0
            
        specified_length = data[offset+1]  # includes null terminator
        str_start = offset + 5
        str_end = str_start
        
        # Find the null terminator
        while str_end < len(data) and data[str_end] != 0:
            str_end += 1
            
        actual_length = (str_end - str_start) + 1  # +1 for the null terminator
        
        if actual_length != specified_length:
            return False, 0, 0, 0
            
        return True, specified_length, str_start, str_end

    def extract_strings(self, binary_file_path: Path) -> List[Dict[str, str]]:
        """
        Extract strings from binary file using the known pattern.
        Returns a list of dicts like [{'orig': '...', 'trans': '...'}, ...].
        """
        data = binary_file_path.read_bytes()
        results = []
        offset = 0
        
        while offset < len(data):
            valid, length, str_start, str_end = self._find_string_pattern(data, offset)
            if valid:
                try:
                    # decode the string (excluding the null terminator)
                    original_str = data[str_start:str_end].decode(self.encoding)
                    results.append({'orig': original_str, 'trans': original_str})
                    offset = str_end + 1  # skip past the null terminator
                    continue
                except UnicodeDecodeError:
                    self.logger.warning(f"Failed to decode string at offset {str_start}.")
            offset += 1
        
        return results

    def replace_strings(self,
                        binary_file_path: Path,
                        translations: List[Dict[str, str]],
                        output_file_path: Path) -> None:
        """
        Replace strings in 'binary_file_path' with corresponding translations (in order).
        Writes result to 'output_file_path'.
        Raises a warning if not all translations are used or if the new strings exceed
        the original pattern's length.
        """
        data = bytearray(binary_file_path.read_bytes())
        offset = 0
        trans_index = 0
        
        while offset < len(data) and trans_index < len(translations):
            valid, old_len, str_start, str_end = self._find_string_pattern(data, offset)
            if valid:
                old_str = None
                try:
                    old_str = data[str_start:str_end].decode(self.encoding)
                except UnicodeDecodeError:
                    self.logger.warning(f"Failed to decode original string at offset {str_start}.")
                
                if old_str is not None:
                    trans_entry = translations[trans_index]
                    if trans_entry['orig'] == old_str:
                        # Prepare the new string
                        new_bytes = trans_entry['trans'].encode(self.encoding)
                        new_len = len(new_bytes) + 1  # account for null terminator
                        
                        # Check if new length exceeds old length
                        if new_len > old_len:
                            self.logger.warning(
                                f"New string length ({new_len}) exceeds old length ({old_len}). "
                                f"Possible data corruption at offset {offset}."
                            )
                            
                        # Rewrite length byte
                        data[offset + 1] = new_len
                        # Overwrite with new bytes
                        data[str_start:str_end] = new_bytes
                        
                        # Move offset forward
                        offset = str_start + new_len
                        trans_index += 1
                        continue
            offset += 1
        
        # Check if all translations were used
        if trans_index < len(translations):
            self.logger.warning(
                f"Not all translations were applied. {len(translations) - trans_index} remaining."
            )
        
        output_file_path.write_bytes(data)

    def process_files(self, mode: Mode) -> None:
        """
        Process all .scb files in 'input_files' directory.
        If mode=EXTRACT, create JSON files in 'json_files'.
        If mode=REPLACE, read JSON from 'json_files' and write modified .scb to 'output_files'.
        """
        if mode == Mode.EXTRACT:
            for file_path in self.input_dir.glob('**/*.scb'):
                try:
                    strings = self.extract_strings(file_path)
                    if strings:
                        json_path = self.json_dir / f"{file_path.stem}.json"
                        with json_path.open('w', encoding='utf-8') as f:
                            json.dump(strings, f, indent=4, ensure_ascii=False)
                        self.logger.info(f"Extracted {len(strings)} strings from {file_path.name}")
                except Exception as e:
                    self.logger.error(f"Error extracting from {file_path}: {e}")
        else:  # Mode.REPLACE
            for json_path in self.json_dir.glob('*.json'):
                try:
                    binary_path = self.input_dir / f"{json_path.stem}.scb"
                    if not binary_path.exists():
                        self.logger.warning(f"No matching binary found for {json_path.stem}.")
                        continue
                    with json_path.open('r', encoding='utf-8') as f:
                        translations = json.load(f)
                    
                    output_file = self.output_dir / binary_path.name
                    self.replace_strings(binary_path, translations, output_file)
                    self.logger.info(f"Replaced strings in {binary_path.name}")
                except Exception as e:
                    self.logger.error(f"Error replacing from {json_path}: {e}")


def main():
    logging.basicConfig(level=logging.INFO)
    
    print("Select mode:")
    print("1. Extract strings")
    print("2. Replace strings")
    
    while True:
        choice = input("Enter choice (1 or 2): ").strip()
        if choice in ('1', '2'):
            break
        print("Invalid choice. Please enter 1 or 2.")
    
    mode = Mode.EXTRACT if choice == '1' else Mode.REPLACE
    
    tool = StringTool()
    try:
        tool.process_files(mode)
        print("Processing complete!")
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == '__main__':
    main()

