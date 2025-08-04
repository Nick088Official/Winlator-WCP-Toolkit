# Logic to convert official vkd3d-proton .tar.zst releases

import os, re, tarfile, json, shutil, zstandard as zstd

from .archive import create_wcp_archive

def extract_version_from_filename(filename):
    # Parses the filename to find the vkd3d-proton version string
    version_match = re.search(r'v?([0-9]+\.[0-9]+(\.[0-9]+)?)', filename)
    return version_match.group(1) if version_match else "unknown"

def convert(tar_zst_path):
    # Core logic to convert a single vkd3d-proton .tar.zst file
    if not os.path.exists(tar_zst_path) or not tar_zst_path.endswith(".tar.zst"):
        print(f"\n[ERROR] File not found or not a .tar.zst file: {tar_zst_path}"); return

    base_dir = os.path.dirname(tar_zst_path)
    extract_dir = os.path.join(base_dir, "vkd3d_temp_extraction")
    
    try:
        # Decompress the .zst stream and then unpack the tarball.
        print(f"\nExtracting {os.path.basename(tar_zst_path)}...")
        dctx = zstd.ZstdDecompressor()
        with open(tar_zst_path, 'rb') as f:
            with dctx.stream_reader(f) as reader:
                with tarfile.open(fileobj=reader, mode='r|') as tar:
                    tar.extractall(path=extract_dir)

        work_dir = os.path.join(extract_dir, os.listdir(extract_dir)[0])
        print(f"Working inside: {work_dir}")

        # Rename folders to Winlator standard
        for arch, new_name in [("x86", "syswow64"), ("x64", "system32")]:
            if os.path.exists(os.path.join(work_dir, arch)):
                os.rename(os.path.join(work_dir, arch), os.path.join(work_dir, new_name))
                print(f"Renamed '{arch}' to '{new_name}'.")

        version = extract_version_from_filename(os.path.basename(tar_zst_path))
        print(f"Detected vkd3d-proton Version: {version}")

        # Create the profile manifest
        profile = {"type": "VKD3D", "versionName": version, "versionCode": 0, "description": f"vkd3d-proton-{version}", "files": []}
        dlls = {"system32": ["d3d12", "d3d12core"], "syswow64": ["d3d12", "d3d12core"]}

        # Scan for existing DLLs and add them to the manifest
        print("\nGenerating profile.json...")
        for folder, dll_list in dlls.items():
            for dll in dll_list:
                if os.path.exists(os.path.join(work_dir, folder, f"{dll}.dll")):
                    profile["files"].append({"source": f"{folder}/{dll}.dll", "target": f"${{{folder}}}/{dll}.dll"})
        
        with open(os.path.join(work_dir, "profile.json"), 'w') as f:
            json.dump(profile, f, indent=4)
        
        # Create the final .wcp archive
        output_path = os.path.join(base_dir, os.path.basename(tar_zst_path).replace(".tar.zst", ".wcp"))
        create_wcp_archive(work_dir, output_path)
        print(f"--- Success! Created: {output_path} ---")
    except Exception as e: print(f"\n[ERROR] An error occurred while processing {tar_zst_path}: {e}")
    finally:
        # Clean up the temporary extraction folder
        if os.path.exists(extract_dir): shutil.rmtree(extract_dir)

if __name__ == "__main__":
    # This allows the script to be run standalone
    print("--- vkd3d-proton to .wcp Converter ---")
    convert(input("Enter the full path to the vkd3d-proton .tar.zst file: ").strip().strip('"'))