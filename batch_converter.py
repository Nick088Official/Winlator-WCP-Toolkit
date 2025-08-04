# Scans a folder for compatible archives, converts them, and organizes the results.

import os
import sys
import shutil
import importlib

def import_converter(module_name):
    try:
        # Import the module from the 'scripts' sub-directory.
        module = importlib.import_module(f"scripts.{module_name}")
        return getattr(module, "convert")
    except ImportError as e:
        print(f"[IMPORT ERROR] Could not load 'scripts/{module_name}.py'. Please check for missing files or typos.")
        print(f"   -> Python's error was: {e}")
        return None
    except AttributeError:
        print(f"[IMPORT ERROR] Found 'scripts/{module_name}.py', but could not find the function 'convert' inside it.")
        return None

# Attempt to load all available scripts.
convert_dxvk = import_converter("dxvk_to_wcp")
convert_dxvk_dev = import_converter("dxvk_dev_to_wcp")
convert_vkd3d_proton = import_converter("vkd3d_proton_to_wcp")

def organize_folder(folder_path, source_files):
    """Creates subdirectories and moves processed files for organization."""
    print("\n--- Organizing Files ---")
    output_dir = os.path.join(folder_path, "_wcp_output")
    source_dir = os.path.join(folder_path, "_source_archives")

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(source_dir, exist_ok=True)

    # Move all original source archives.
    for file_path in source_files:
        if os.path.exists(file_path):
            try:
                shutil.move(file_path, source_dir)
            except shutil.Error as e:
                print(f"[WARN] Could not move source file '{os.path.basename(file_path)}': {e}")
    
    # Scan for and move all new .wcp files.
    for filename in os.listdir(folder_path):
        if filename.endswith(".wcp"):
            try:
                shutil.move(os.path.join(folder_path, filename), output_dir)
            except shutil.Error as e:
                print(f"[WARN] Could not move output file '{filename}': {e}")

def main():
    """Main function to run the batch processing and organization."""
    print("--- WCP Batch Converter and Organizer ---")
    folder_path = input("Enter the full path to the folder containing your archives: ").strip().strip('"')

    if not os.path.isdir(folder_path):
        print(f"\n[ERROR] The path provided is not a valid directory: {folder_path}"); sys.exit(1)

    print(f"\nScanning folder: {folder_path}\n")

    try:
        files_in_dir = os.listdir(folder_path)
    except OSError as e:
        print(f"[ERROR] Could not read directory: {e}"); sys.exit(1)
        
    processed_count = 0
    source_files_to_move = []
    
    for filename in files_in_dir:
        full_path, processed = os.path.join(folder_path, filename), False
        if not os.path.isfile(full_path): continue

        # Dispatch the file to the appropriate converter based on its extension.
        if filename.endswith(".tar.gz") and convert_dxvk:
            print("-" * 50); print(f"Found DXVK Release file: {filename}")
            convert_dxvk(full_path); processed = True
        elif filename.endswith(".zip") and convert_dxvk_dev:
            print("-" * 50); print(f"Found DXVK Dev file: {filename}")
            convert_dxvk_dev(full_path); processed = True
        elif filename.endswith(".tar.zst") and convert_vkd3d_proton:
            print("-" * 50); print(f"Found vkd3d-proton file: {filename}")
            convert_vkd3d_proton(full_path); processed = True
        
        if processed:
            processed_count += 1
            source_files_to_move.append(full_path)
            print("-" * 50)
            
    if processed_count > 0:
        print(f"\nBatch processing complete. Processed {processed_count} file(s).")
        organize_folder(folder_path, source_files_to_move)
    else:
        print("\nNo compatible files (.tar.gz, .zip, .tar.zst) were found to process.")

if __name__ == "__main__":
    main()