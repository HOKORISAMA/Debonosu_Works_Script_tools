import os

def read_file_as_byte_array(file_path, encoding='shift_jis'):
    try:
        with open(file_path, 'rb') as file:
            byte_array = bytearray(file.read())
        return byte_array.decode(encoding, errors='ignore')
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file {file_path}: {e}")
        return None

def compare_scb_files(file1, file2, chunk_size=4096):
    differing_indices = []  # List to store differing indices
    
    try:
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            while True:
                chunk1 = f1.read(chunk_size)
                chunk2 = f2.read(chunk_size)
                
                # If both chunks are empty, end of both files has been reached
                if not chunk1 and not chunk2:
                    break
                
                # If chunks have different lengths, files are different
                if len(chunk1) != len(chunk2):
                    print(f"Files {file1} and {file2} have different lengths.")
                    return
                
                # Compare the chunks
                for i, (byte1, byte2) in enumerate(zip(chunk1, chunk2)):
                    if byte1 != byte2:
                        differing_indices.append((f1.tell() - len(chunk1) + i, byte1, byte2))
                
    except FileNotFoundError as e:
        print(f"File not found: {e.filename}")
        return
    except Exception as e:
        print(f"An error occurred while comparing files: {e}")
        return
    
    if differing_indices:
        print(f"The content of the files {file1} and {file2} does not match.")
        for index, byte1, byte2 in differing_indices:
            print(f"Difference found at index {index}: '{byte1}' in file1, '{byte2}' in file2")
    else:
        print(f"The content of the files {file1} and {file2} matches.")

def compare_files_in_folders(folders, chunk_size=4096):
    files_dict = {}
    
    # Collect all files from the folders
    for folder in folders:
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith('.scb'):  # Only compare .scb files
                    full_path = os.path.join(root, file)
                    if file not in files_dict:
                        files_dict[file] = []
                    files_dict[file].append(full_path)
    
    # Compare the files with the same name from different folders
    for filename, file_paths in files_dict.items():
        num_files = len(file_paths)
        for i in range(num_files):
            for j in range(i + 1, num_files):
                file1 = file_paths[i]
                file2 = file_paths[j]
                print(f"\nComparing {file1} and {file2}:")
                compare_scb_files(file1, file2, chunk_size)

# Example usage:
folders = ["input_scb_files", "new_scb_files"]
compare_files_in_folders(folders)
