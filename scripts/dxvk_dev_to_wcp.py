# Logic to convert DXVK development .zip releases

import os, json, shutil, zipfile

from .archive import create_wcp_archive

def convert(zip_path):
    # Core logic to convert a single DXVK-dev .zip file
    if not os.path.exists(zip_path) or not zip_path.endswith(".zip"):
        print(f"\n[ERROR] File not found or not a .zip file: {zip_path}"); return

    # Get version info from the user since dev build filenames are inconsistent
    print(f"\nProcessing Dev Build: {os.path.basename(zip_path)}")
    version_name = input("Enter DXVK version name (e.g., 2.3-sarek-f1a3b4c): ")
    while True:
        try: version_code = int(input("Enter a numeric version code (e.g., 20231026): ")); break
        except ValueError: print("[ERROR] Please enter a valid number.")

    base_dir = os.path.dirname(zip_path)
    extract_dir = os.path.join(base_dir, "dxvk_dev_temp_extraction")
    
    try:
        # Unpack the archive
        print(f"\nExtracting {os.path.basename(zip_path)}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref: zip_ref.extractall(extract_dir)
        work_dir = extract_dir # ZIPs often extract directly without a subfolder

        # Rename folders to Winlator standard
        for arch, new_name in [("x32", "syswow64"), ("x64", "system32")]:
            if os.path.exists(os.path.join(work_dir, arch)):
                os.rename(os.path.join(work_dir, arch), os.path.join(work_dir, new_name))
                print(f"Renamed '{arch}' to '{new_name}'.")

        # Create the profile manifest
        profile = {"type": "DXVK", "versionName": version_name, "versionCode": version_code, "description": f"DXVK-{version_name}", "files": []}
        dlls = {"system32": ["d3d9", "d3d10", "d3d10_1", "d3d10core", "d3d11", "dxgi"], "syswow64": ["d3d8", "d3d9", "d3d10", "d3d10_1", "d3d10core", "d3d11", "dxgi"]}

        # Scan for existing DLLs and add them to the manifest
        print("\nGenerating profile.json...")
        for folder, dll_list in dlls.items():
            for dll in dll_list:
                if os.path.exists(os.path.join(work_dir, folder, f"{dll}.dll")):
                    profile["files"].append({"source": f"{folder}/{dll}.dll", "target": f"${{{folder}}}/{dll}.dll"})
        
        with open(os.path.join(work_dir, "profile.json"), 'w') as f:
            json.dump(profile, f, indent=4)
        
        # Create the final .wcp archive
        output_path = os.path.join(base_dir, f"dxvk-{version_name}-{version_code}.wcp")
        create_wcp_archive(work_dir, output_path)
        print(f"--- Success! Created: {output_path} ---")
    except Exception as e: print(f"\n[ERROR] An error occurred while processing {zip_path}: {e}")
    finally:
        # Clean up the temporary extraction folder
        if os.path.exists(extract_dir): shutil.rmtree(extract_dir)

if __name__ == "__main__":
    # This allows the script to be run standalone
    print("--- DXVK-Dev (ZIP) to .wcp Converter ---")
    convert(input("Enter the full path to the DXVK .zip file: ").strip().strip('"'))