# script to fetch all recent, compatible release tags from the official Box64 repository and trigger the 'Compile-Box64.yml' workflow in a personal fork for each tag.

import sys, subprocess, json, time, shutil

# --- CONFIGURATION ---
MINIMUM_COMPATIBLE_TAG = "v0.2.8"

def run_gh_command(command_list):
    """Executes a GitHub CLI command and handles errors."""
    try:
        result = subprocess.run(command_list, check=True, capture_output=True, text=True, encoding='utf-8')
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        stderr = e.stderr.strip() if hasattr(e, 'stderr') else "gh command not found."
        print(f"\n[ERROR] Command failed: {' '.join(command_list)}\n--- STDERR ---\n{stderr}")
        return None

def main():
    """Main function to run the batch build trigger."""
    if not shutil.which("gh"): print("[FATAL ERROR] GitHub CLI ('gh') is not installed."); sys.exit(1)
    if run_gh_command(["gh", "auth", "status"]) is None: print("[FATAL ERROR] Not logged in to GitHub CLI. Please run 'gh auth login'."); sys.exit(1)

    print("--- Box64 Batch Build Trigger ---")
    username = input("Enter your GitHub username: ")
    fork_name = input("Enter the name of your forked Box64 repository (usually 'box64'): ")
    repo_path = f"{username}/{fork_name}"
    workflow_name = "Compile-Box64.yml"

    print("\nFetching all release tags from the official ptitSeb/box64 repository...")
    
    release_list_json = run_gh_command(["gh", "release", "list", "--repo", "ptitSeb/box64", "--json", "tagName"])
    if release_list_json is None: sys.exit(1)
        
    try:
        releases = json.loads(release_list_json)
        # Filter for official release tags AND ensure they meet the minimum version requirement.
        tags_to_build = [
            release['tagName'] for release in releases 
            if release['tagName'].startswith('v') and release['tagName'] >= MINIMUM_COMPATIBLE_TAG
        ]
    except json.JSONDecodeError:
        print("[FATAL ERROR] Failed to parse the list of releases from GitHub."); sys.exit(1)

    if not tags_to_build:
        print(f"[ERROR] No compatible release tags found from {MINIMUM_COMPATIBLE_TAG} onwards. Aborting."); sys.exit(1)

    print(f"Found {len(tags_to_build)} compatible release tags to build (from {MINIMUM_COMPATIBLE_TAG} onwards).")
    print("The script will now trigger a workflow for each tag.")
    print("-" * 50); time.sleep(3)

    for tag in sorted(tags_to_build): # Sort to ensure chronological build order
        print(f"--> Triggering workflow for tag: {tag}")
        
        trigger_command = [
            "gh", "workflow", "run", workflow_name,
            "--repo", repo_path,
            "--ref", "main",
            "-f", f"box64_version_ref={tag}"
        ]
        
        if run_gh_command(trigger_command) is not None:
            print(f"    Workflow for {tag} triggered successfully.")
            print("    Waiting 30 seconds to avoid overwhelming the API...")
            time.sleep(30)
        else:
            print(f"    Failed to trigger workflow for {tag}. Continuing...")
    
    print("-" * 50)
    print("All build workflows have been triggered successfully!")
    print("Check your repository's 'Actions' tab to monitor their progress and download the artifacts.")

if __name__ == "__main__":
    main()