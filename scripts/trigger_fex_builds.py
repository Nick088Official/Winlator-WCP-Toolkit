# remotely build specific FEX tags, commits, or the latest main branch.

import sys, subprocess, json, time, shutil

MINIMUM_COMPATIBLE_TAG = "FEX-2507" # Older tags use an incompatible build system.

def run_gh_api_command(endpoint, method="GET", raw_body=None):
    """Executes a GitHub API command using 'gh', supporting passing data via stdin."""
    command = ["gh", "api", endpoint, "--method", method]
    if raw_body: command.extend(["--input", "-"])
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8', input=raw_body)
        return json.loads(result.stdout) if result.stdout else {}
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        stderr = e.stderr.strip() if hasattr(e, 'stderr') else "gh command not found."
        print(f"\n[ERROR] API command failed for {endpoint}:\n--- STDERR ---\n{stderr}"); return None
    except json.JSONDecodeError: print(f"\n[ERROR] Failed to parse JSON response from {endpoint}"); return None

def trigger_build(repo_path, build_branch, ref_name, commit_sha, custom_files):
    """Core logic to trigger a single build for a given commit."""
    print(f"\n--> Preparing to build ref: {ref_name} (Commit: {commit_sha[:7]})")
    
    print("    1. Fetching base tree from the commit..."); base_tree = run_gh_api_command(f"/repos/FEX-Emu/FEX/git/trees/{commit_sha}");
    if base_tree is None: return False
    
    print("    2. Creating new merged tree via API..."); new_tree_payload = {"base_tree": base_tree["sha"], "tree": list(custom_files.values())}
    created_tree = run_gh_api_command(f"/repos/{repo_path}/git/trees", "POST", raw_body=json.dumps(new_tree_payload))
    if created_tree is None: return False

    print("    3. Creating new commit via API..."); commit_payload = {"message": f"Build: Prepare FEX tag {ref_name}", "tree": created_tree["sha"], "parents": [commit_sha]}
    new_commit = run_gh_api_command(f"/repos/{repo_path}/git/commits", "POST", raw_body=json.dumps(commit_payload))
    if new_commit is None: return False

    print(f"    4. Updating '{build_branch}' branch to trigger build..."); update_payload = {"sha": new_commit["sha"], "force": True}
    run_gh_api_command(f"/repos/{repo_path}/git/refs/heads/{build_branch}", "PATCH", raw_body=json.dumps(update_payload))
    
    print(f"    Workflow for {ref_name} triggered successfully.")
    return True

def main():
    if not shutil.which("gh"): print("[FATAL ERROR] GitHub CLI ('gh') is not installed."); sys.exit(1)
    if run_gh_api_command("user") is None: print("[FATAL ERROR] Not logged in to GitHub CLI. Please run 'gh auth login'."); sys.exit(1)

    print("--- FEX-Emu Remote Build Trigger ---")
    username = input("Enter your GitHub username: ")
    fork_name = input("Enter the name of your forked FEX repository (usually 'FEX'): ")
    repo_path, build_branch = f"{username}/{fork_name}", "ci-test"

    print("\nFetching all tags from the official FEX-Emu repository...")
    tags_data = run_gh_api_command("/repos/FEX-Emu/FEX/tags?per_page=100")
    if tags_data is None: sys.exit(1)
    all_tags = {tag['name']: tag['commit']['sha'] for tag in tags_data if tag['name'].startswith('FEX-')}
    
    print(f"Fetching custom build files from '{build_branch}' branch...")
    ci_branch = run_gh_api_command(f"/repos/{repo_path}/branches/{build_branch}")
    if ci_branch is None: print(f"[FATAL ERROR] Could not find the '{build_branch}' branch."); sys.exit(1)
    
    ci_tree = run_gh_api_command(f"/repos/{repo_path}/git/trees/{ci_branch['commit']['sha']}?recursive=1")
    if ci_tree is None: sys.exit(1)
    
    files_to_find = [".github/workflows/Compile-FEXCore.yml", "Data/nix/cmake_configure_woa32.sh", "Data/nix/cmake_configure_woa64.sh"]
    custom_files = {item["path"]: item for item in ci_tree["tree"] if item["path"] in files_to_find}

    if len(custom_files) != len(files_to_find): print("[FATAL ERROR] Could not find all custom build files."); sys.exit(1)
    print("Successfully located custom workflow and build scripts.")

    while True:
        print("\n" + "-" * 50)
        print("Select a build mode:")
        print(f"  1. Build ALL compatible tags (from {MINIMUM_COMPATIBLE_TAG} onwards)")
        print( "  2. Build a SINGLE specific tag")
        print( "  3. Build a specific commit or latest `main` (Nightly)")
        print( "  q. Quit")
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            tags_to_build = sorted([t for t in all_tags.keys() if t >= MINIMUM_COMPATIBLE_TAG])
            print(f"\nFound {len(tags_to_build)} compatible tags to build.")
            for tag_name in tags_to_build:
                success = trigger_build(repo_path, build_branch, tag_name, all_tags[tag_name], custom_files)
                if success: print(f"    Waiting 60 seconds before next tag..."); time.sleep(60)
            print("\nAll build workflows have been triggered.")
            
        elif choice == '2':
            tag_input = input("Enter the specific tag to build (e.g., FEX-2508): ").strip()
            if tag_input not in all_tags: print(f"[ERROR] Tag '{tag_input}' not found.")
            elif tag_input < MINIMUM_COMPATIBLE_TAG: print(f"[ERROR] Tag '{tag_input}' is too old. Please choose {MINIMUM_COMPATIBLE_TAG} or newer.")
            else: trigger_build(repo_path, build_branch, tag_input, all_tags[tag_input], custom_files)
        
        elif choice == '3':
            commit_input = input("Enter a commit hash or type 'main' for the latest nightly build: ").strip()
            if commit_input.lower() == 'main':
                print("Fetching latest commit from main branch...")
                main_branch_info = run_gh_api_command("/repos/FEX-Emu/FEX/branches/main")
                if main_branch_info:
                    commit_sha = main_branch_info["commit"]["sha"]
                    trigger_build(repo_path, build_branch, f"main-{commit_sha[:7]}", commit_sha, custom_files)
            else:
                #  resolve the user's short 7 character hash to the full 40-character SHA.
                if len(commit_input) < 7:
                    print("[ERROR] Invalid commit hash format. Must be at least 7 characters.")
                else:
                    print(f"Resolving commit hash '{commit_input}'...")
                    # GitHub API allows using a short hash to get a commit's details.
                    commit_info = run_gh_api_command(f"/repos/FEX-Emu/FEX/commits/{commit_input}")
                    if commit_info and "sha" in commit_info:
                        # 'sha' field in the response contains the full 40-character hash.
                        full_commit_sha = commit_info["sha"]
                        print(f"Found full commit: {full_commit_sha}")
                        # pass the full hash to our trigger function.
                        trigger_build(repo_path, build_branch, f"main-{commit_input[:7]}", full_commit_sha, custom_files)
                    else:
                        print(f"[ERROR] Could not find commit matching '{commit_input}' in the official repository.")

        elif choice.lower() == 'q': break
        else: print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()