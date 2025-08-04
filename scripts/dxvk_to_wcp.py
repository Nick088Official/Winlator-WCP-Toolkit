# Logic to convert official DXVK .tar.gz releases

import os, re, tarfile, json, shutil

from .archive import create_wcp_archive

def extract_version_from_filename(filename):
    # Intelligently parses the filename to find the DXVK version string
    filename_lower = filename.lower()
    version_match = re.search(r'v?([0-9]+\.[0-9]+(\.[0-9]+)?)', filename_lower)
    core_version = version_match.group(1) if version_match else "unknown"
    prefixes = []
    if "sarek" in filename_lower: prefixes.append("sarek")
    if "gplasync" in filename_lower: prefixes.append("gplasync")
    elif "async" in filename_lower: prefixes.append("async")
    return "-".join(prefixes) + "-" + core_version if prefixes else core_version

def convert(tar_path):
    # Core logic to convert a single DXVK .tar.gz file
    if not os.path.exists(tar_path) or not tar_path.endswith(".tar.gz"):
        print(f"\n[ERROR] File not found or not a .tar.gz file: {tar_path}"); return

    base_dir = os.path.dirname(tar_path)
    extract_dir = os.path.join(base_dir, "dxvk_temp_extraction")
    
    try:
        # Unpack the archive
        print(f"\nExtracting {os.path.basename(tar_path)}...")
        with tarfile.open(tar_path, 'r:gz') as tar: tar.extractall(path=extract_dir)
        work_dir = os.path.join(extract_dir, os.listdir(extract_dir)[0])
        print(f"Working inside: {work_dir}")

        # Rename folders to Winlator standard
        for arch, new_name in [("x32", "syswow64"), ("x64", "system32")]:
            if os.path.exists(os.path.join(work_dir, arch)):
                os.rename(os.path.join(work_dir, arch), os.path.join(work_dir, new_name))
                print(f"Renamed '{arch}' to '{new_name}'.")

        version = extract_version_from_filename(os.path.basename(tar_path))
        print(f"Detected DXVK Version: {version}")
        
        # Create the profile manifest
        profile = {"type": "DXVK", "versionName": version, "versionCode": 0, "description": f"DXVK-{version}", "files": []}
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
        output_path = os.path.join(base_dir, os.path.basename(tar_path).replace(".tar.gz", ".wcp"))
        create_wcp_archive(work_dir, output_path)
        print(f"--- Success! Created: {output_path} ---")
    except Exception as e: print(f"\n[ERROR] An error occurred while processing {tar_path}: {e}")
    finally:
        # Clean up the temporary extraction folder
        if os.path.exists(extract_dir): shutil.rmtree(extract_dir)

if __name__ == "__main__":
    # This allows the script to be run standalone
    print("--- DXVK (Official Release) to .wcp Converter ---")
    convert(input("Enter the full path to the DXVK .tar.gz file: ").strip().strip('"'))