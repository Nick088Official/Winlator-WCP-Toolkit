#!/data/data/com.termux/files/usr/bin/bash

# --- Global Variables ---
DOWNLOAD_DIR=~/storage/shared/Download
TEMP_DIR=~/wcp_temp_extraction

# --- Helper Functions ---
print_header() {
    clear
    echo "=========================================="
    echo "     Winlator WCP Toolkit for Android     "
    echo "=========================================="
    echo
}

# --- Core Logic ---
initial_setup() {
    print_header
    echo "Performing first-time setup... This may take a few minutes."
    pkg update -y && pkg upgrade -y
    # jq is a powerful command-line JSON processor, essential for this script.
    pkg install -y git tar zstd binutils python jq -y
    termux-setup-storage
    echo "Waiting for you to grant storage permission..."
    while [ ! -d "$DOWNLOAD_DIR" ]; do sleep 2; done
    echo "Storage permission granted!"; sleep 2
}

# Universal conversion logic for tar-based archives
# $1: Full path to the archive file
# $2: Component type (DXVK, VKD3D-proton)
# $3: List of DLLs for system32
# $4: List of DLLs for syswow64
# $5: Decompression program for tar (e.g., 'gunzip', 'unzstd')
convert_component() {
    local archive_path="$1" comp_type="$2" dlls_system32="$3" dlls_syswow64="$4" decompress_prog="$5"
    local filename=$(basename "$archive_path")
    # Extract version from filename 
    local version=$(echo "$filename" | sed -n 's/.*-\([0-9]\+\.[0-9.]\+\)\.tar\..*/\1/p')
    if [[ -z "$version" ]]; then version="unknown"; fi

    echo "--- Processing: $filename ---"
    rm -rf "$TEMP_DIR"; mkdir -p "$TEMP_DIR"

    echo "Extracting archive..."
    tar --use-compress-program="$decompress_prog" -xf "$archive_path" -C "$TEMP_DIR"
    local work_dir="$TEMP_DIR/$(ls "$TEMP_DIR")"
    
    # Standardize folder names
    [ -d "$work_dir/x64" ] && mv "$work_dir/x64" "$work_dir/system32"
    [ -d "$work_dir/x32" ] && mv "$work_dir/x32" "$work_dir/syswow64" # For DXVK
    [ -d "$work_dir/x86" ] && mv "$work_dir/x86" "$work_dir/syswow64" # For vkd3d-proton

    # Create profile.json from a template using jq
    local profile_path="$work_dir/profile.json"
    echo "Generating profile.json..."
    jq -n --arg type "$comp_type" --arg name "$version" --arg desc "$comp_type-$version" \
      '{type: $type, versionName: $name, versionCode: 0, description: $desc, files: []}' > "$profile_path"

    # Add file entries to the profile manifest
    for dll in $dlls_system32; do
        if [ -f "$work_dir/system32/$dll.dll" ]; then
            jq --arg src "system32/$dll.dll" --arg tgt "\${system32}/$dll.dll" '.files += [{"source":$src, "target":$tgt}]' "$profile_path" >tmp.json && mv tmp.json "$profile_path"
        fi
    done
    for dll in $dlls_syswow64; do
        if [ -f "$work_dir/syswow64/$dll.dll" ]; then
            jq --arg src "syswow64/$dll.dll" --arg tgt "\${syswow64}/$dll.dll" '.files += [{"source":$src, "target":$tgt}]' "$profile_path" >tmp.json && mv tmp.json "$profile_path"
        fi
    done
    
    # Create the final .wcp archive
    local output_file="${filename%.tar.*}.wcp"
    echo "Creating $output_file..."
    (cd "$work_dir" && tar --use-compress-program=zstd -cf "$DOWNLOAD_DIR/$output_file" ./*)
    
    echo "--- Success! Created $output_file in your Downloads folder. ---"
    rm -rf "$TEMP_DIR"
}

batch_process() {
    print_header
    echo "Starting Batch Conversion... Looking for archives in: $DOWNLOAD_DIR"
    local processed_count=0; local source_files_to_move=()

    for file in "$DOWNLOAD_DIR"/*; do
        if [[ ! -f "$file" ]]; then continue; fi
        
        local processed=false
        if [[ "$file" == *.tar.gz ]]; then
            convert_component "$file" "DXVK" "d3d9 d3d10 d3d10_1 d3d10core d3d11 dxgi" "d3d8 d3d9 d3d10 d3d10_1 d3d10core d3d11 dxgi" "gunzip"
            processed=true
        elif [[ "$file" == *.tar.zst ]]; then
            convert_component "$file" "VKD3D" "d3d12 d3d12core" "d3d12 d3d12core" "unzstd"
            processed=true
        fi
        
        if [[ "$processed" == true ]]; then
            processed_count=$((processed_count + 1))
            source_files_to_move+=("$file")
        fi
    done

    if [[ "$processed_count" -gt 0 ]]; then
        echo -e "\nBatch processing complete. Processed $processed_count file(s)."
        organize_downloads "${source_files_to_move[@]}"
    else
        echo "No compatible archives (.tar.gz, .tar.zst) found in your Downloads folder."
    fi
    echo -e "\nPress Enter to return to the menu."; read
}

organize_downloads() {
    local source_files=("$@")
    local output_dir="$DOWNLOAD_DIR/_wcp_output"; local source_dir="$DOWNLOAD_DIR/_source_archives"
    mkdir -p "$output_dir" "$source_dir"
    
    echo "Organizing files..."
    for file in "${source_files[@]}"; do mv "$file" "$source_dir/" 2>/dev/null; done
    for wcp_file in "$DOWNLOAD_DIR"/*.wcp; do
        if [ -f "$wcp_file" ]; then mv "$wcp_file" "$output_dir/" 2>/dev/null; fi
    done
    echo "Moved .wcp files to '_wcp_output' and source archives to '_source_archives'."
}

# --- Main Menu ---
main_menu() {
    print_header
    echo "Please place your archives (.tar.gz, .tar.zst) in your phone's"
    echo "main 'Download' folder before starting."
    echo -e "\nSelect an option:"
    echo " 1. Batch Convert All Files in Download Folder"
    echo " q. Quit"
    echo
    read -p "Enter your choice: " choice

    case $choice in
        1) batch_process ;;
        q|Q) echo "Exiting."; exit 0 ;;
        *) echo "Invalid choice. Press Enter to try again."; read ;;
    esac
}

# --- Script Entry Point ---
# Run setup only once by creating a hidden marker file
if [ ! -f ~/.wcp_tools_setup_complete ]; then
    initial_setup
    touch ~/.wcp_tools_setup_complete
fi

# Show the menu in a loop until the user quits
while true; do
    main_menu
done