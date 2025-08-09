# Winlator WCP Toolkit

A toolkit for Windows & Android users to package various Winlator contents like DXVK, vkd3d-proton, and FEX-Emu into `.wcp` files. This contains both info related to `.wcp` files, where to find them, and code for conversions.

**NOTE: THIS REPOSITORY IS MAINLY FOR WINLATOR BIONIC FORKS**

---


## What is `.wcp`?

.wcp is the file extension for add-ons. It is compressed using XZ or Zstd and includes a profile.json file as a manifest. You can create your own add-on files containing various contents. Since these files often include executable programs, make sure to verify that add-ons from other sources do not contain malicious software before installation.

## Want Pre-converted `.wcp` files?
This GitHub Repository is about information on what exactly and how to make `.wcp` files.
All compiled packages are available in the repository:
### -> [Winlator-WCP-Collections](https://github.com/Nick088Official/Winlator-WCP-Collections) <-

---

## Features

- **Conversion:** Convert pre-compiled files to `.wcp`.
- **Platform Support:** Windows & Android (Termux).
- **Contents Support:** DXVK (Official, Sarek, Async, Gplasync), vkd3d-proton and FEXCore (partially).
- **Documented Information:** about FEXCore, how to install, the different dvxk versions.
- **Batch Processing:** A master script (`batch_converter.py`) can scan and convert an entire folder of archives at once, then organize the results.
- **Modular and Expandable:** The project is structured to easily add new scripts for other contents in the future, possibly.


## Installation & Setup


### Android (Termux)

1.  Get Termux from [F-Droid](https://f-droid.org/).
2.  Open Termux and paste the following command. This will download the script and run it.
    ```sh
    curl -sL https://raw.githubusercontent.com/Nick088Official/Winlator-WCP-Toolkit/refs/heads/master/wcp_tools.sh | bash
    ```
    The script will perform a one-time setup, installing all necessary tools and asking for storage permission. Please grant it.

3.  Download the precompiled archives you want to convert (check [here](https://github.com/Nick088Official/Winlator-WCP-Toolkit/?tab=readme-ov-file#finding-pre-compiled-component-files)) and make sure they are in your phone's main `/Download` folder.
4.  After setup, a menu will appear. Choose the "Batch Convert" option. The script will find all compatible files in your `Download` folder, convert them, and organize the results automatically.



## Windows

#### Prerequisites
-   **Python 3.x:** Download from [python.org](https://www.python.org/downloads/). **Crucially, check the box that says "Add Python to PATH"** during installation.
-   **Git:** (Optional) Download from [git-scm.com](https://git-scm.com/downloads).

#### Project Setup
1.  Get the Repository, either via:
    -   **Git:** Clone the repository via CMD:
        ```sh
        git clone https://github.com/Nick088Official/Winlator-WCP-Toolkit.git
        ```
    - or just **download** the zip file from [here](https://github.com/Nick088Official/Winlator-WCP-Toolkit/archive/refs/heads/master.zip) and unzip it
2.  **Navigate to the project directory:**
    ```sh
    cd Winlator-WCP-Toolkit
    ```
3.  **Install required Python libraries:**
    ```sh
    pip install -r requirements.txt
    ```

### Usage

#### The Easy Way: Batch Converting Downloaded Files

This is the recommended method for most users.

**Script:** `batch_converter.py`

1.  **Download Files:** Get pre-compiled archives from [here](https://github.com/Nick088Official/Winlator-WCP-Toolkit/?tab=readme-ov-file#finding-pre-compiled-component-files). Place them all into a single folder (e.g., `C:\Users\YourUser\Downloads\WCP_Staging`).
2.  **Run the Script:**
    ```sh
    python batch_converter.py
    ```
3.  **Provide the Path:** When prompted, enter the full path to the folder containing your archives.
4.  The script will convert everything and then neatly organize the folder, moving the `.wcp` files to `_wcp_output` and the original archives to `_source_archives`.



---

## How to Use the `Compile-FEXCore.yml` Workflow (Advanced)

This section documents an advanced method for building your own FEX DLLs for Windows on ARM using GitHub's servers. The process is semi-automated, with a one-time setup and a single, cross-platform Python script to trigger builds.

### Why are older FEX versions not supported?
The FEX-Emu project's build system has evolved significantly over time. The custom build scripts used in this workflow are based on the **modern** FEX structure. Older tags (before `FEX-2507`) used a different system and are missing key files that the modern scripts require. Attempting to compile old code with modern build instructions will fail.

### Step 1: Prepare Your Repository (One-Time Setup)

1.  **Fork the Repository:** Go to **https://github.com/FEX-Emu/FEX** and click the **"Fork"** button. Don't copy only the `main` branch.
2.  **Create a Build Branch:** In your forked repository, create a new branch named **`ci-test`** from the `main` branch.
3.  **Set as Default Branch:** Go to your fork's **Settings -> Branches**. Under "Default branch", switch from `main` to **`ci-test`** and click "Update".
4.  **Add/Modify Files:** In your `ci-test` branch, make the following changes:
    -   Add the **[`Compile-FEXCore.yml`](https://raw.githubusercontent.com/Nick088Official/Winlator-WCP-Toolkit/master/scripts/Compile-FEXCore.yml)** file to a new `.github/workflows/` directory.
    -   Edit `Data/nix/cmake_configure_woa32.sh` and `Data/nix/cmake_configure_woa64.sh`. In each file, find the line that starts with `cmake $FEX_CMAKE_TOOLCHAIN...` and add the flag `-DTUNE_CPU=none` to the end of that line.
5.  **Commit** these changes to your `ci-test` branch. Your fork is now a dedicated "build machine".

### Step 2: Running the Build Automation Script

The provided Python script works on **Windows, Linux, macOS, and Android (Termux)** to remotely instruct your fork to build specific versions.

#### A Note on Commit Hashes
When the script asks you to build a specific commit, you **only need to provide the short hash** (the first 7 characters, e.g., `095b2a8`). This is easier to copy and is all that's needed to identify the exact version, as the script will automatically get the 40 full character commit.

1.  **Prerequisites:**
    -   **Python:** Must be installed.
    -   **GitHub CLI:** Must be installed.
        -   On Windows/macOS/Linux, see the [official guide](https://cli.github.com/).
        -   On Termux, run `pkg install python git gh`.
    -   **Authentication:** You must be logged in to your GitHub account. Open a terminal and run `gh auth login`.

2.  **Run the Automation Script:**
    Choose the method that best fits your platform.

    #### On Android (Quick Script Method)
    This is the recommended method for Termux as it only downloads the single script you need, saving space.
    1.  Download the script using `curl`:
        ```sh
        curl -O https://raw.githubusercontent.com/YourUsername/Winlator-WCP-Toolkit/main/scripts/trigger_fex_builds.py
        ```
    2.  Run the script:
        ```sh
        python trigger_fex_builds.py
        ```

    #### On Windows (Full Toolkit Method)
    This is the recommended method for PC users as it downloads the entire toolkit.
    1.  Clone the repository and navigate into it:
        ```sh
        git clone https://github.com/YourUsername/Winlator-WCP-Toolkit.git
        cd Winlator-WCP-Toolkit
        ```
    2.  Run the script:
        ```sh
        python scripts/trigger_fex_builds.py
        ```

    After running the script with either method, it will present a menu with several options.

3.  **Build Modes Explained:**
    -   **Build ALL compatible tags:** Finds and builds all FEX tags from `FEX-2507` onwards.
    -   **Build a SINGLE specific tag:** Prompts for a tag name (e.g., `FEX-2508`).
    -   **Build a specific commit or latest `main` (Nightly):**
        -   Enter a **commit hash** (e.g., `a1b2c3d`) to build a specific unreleased version.
        -   Enter **`main`** to build the very latest code from the official FEX repository.

### Step 3: Downloading the Artifact
After any workflow is complete, go to its summary page in your fork's "Actions" tab. At the bottom, under the **"Artifacts"** section, you will find a `.zip` file containing the compiled `.dll` files and the final `.wcp` package.



---

## General Information

### Finding Pre-Compiled Component Files

| Component | Download From | File to Get |
| :--- | :--- | :--- |
| **Official DXVK** | [github.com/doitsujin/dxvk/releases](https://github.com/doitsujin/dxvk/releases) | The `.tar.gz` file (e.g., `dxvk-2.3.tar.gz`) |
| **DXVK Nightly/Dev**| [DXVK GitHub Actions](https://github.com/doitsujin/dxvk/actions/workflows/artifacts.yml) | `dxvk-master.zip` (from the latest `master` run) |
| **DXVK-Sarek** | [github.com/pythonlover02/DXVK-Sarek/releases](https://github.com/pythonlover02/DXVK-Sarek/releases) | The `.tar.gz` file |
| **DXVK-GPLAsync** | [https://gitlab.com/Ph42oN/dxvk-gplasync/-/releases](https://github.com/pythonlover02/DXVK-Sarek/releases) | The `.tar.gz` file |
| **vkd3d-proton** | [github.com/HansKristian-Work/vkd3d-proton/releases](https://github.com/HansKristian-Work/vkd3d-proton/releases) | The `.tar.zst` file |
| **FEX-Emu (Linux)** | [TGP-17's Fork FEX GitHub Actions](https://github.com/TGP-17/FEX/actions/workflows/Compile-FEXCore.yml) (or check ([HERE](https://github.com/Nick088Official/Winlator-WCP-Toolkit/?tab=readme-ov-file#how-to-use-the-compile-fexcoreyml-workflow-advanced)) | `FEXCore DLLs.zip` |
| **Official DXVK** | [github.com/doitsujin/dxvk/releases](https://github.com/doitsujin/dxvk/releases) | The `.tar.gz` file (e.g., `dxvk-2.3.tar.gz`) |


### How the WCP Conversion Works
1.  **Extract:** The initial archive is unpacked into a temporary folder.
2.  **Organize:** Files are reorganized into the structure Winlator expects.
    -   **DXVK:** Renames `x64`/`x32` folders to `system32`/`syswow64`.
    -   **vkd3d-proton:** Renames `x64`/`x86` folders to `system32`/`syswow64`.
    -   **FEX DLLs:** Copies both the 32-bit (`libwow64fex.dll`) and 64-bit (`libarm64ecfex.dll`) files into a single `system32` folder.
3.  **Manifest (`profile.json`):** A JSON file is generated telling Winlator the component `type`, `version`, and where to place every file.
4.  **Archive:** All organized files and the manifest are bundled into a `.tar` archive and compressed with Zstandard, creating the final `.wcp` file.


### Choosing the Right DXVK Version

| DXVK Version | Primary Purpose | Best For... | Potential Downsides |
| :--- | :--- | :--- | :--- |
| **Official DXVK** | The standard, stable version. | **Most users.** This should always be your starting point. | Can have noticeable stutter the first time a new effect or area is shown in-game. |
| **Nightly/Dev Builds** | The absolute latest, unreleased code with bleeding-edge fixes. | Testing a fix for a specific game that is broken on the stable release. | Potentially unstable and may introduce new bugs. Use for troubleshooting only. |
| **DXVK-Async** | Reduces stutter by compiling shaders on a background thread. | Games with heavy, constant stutter (e.g., Unreal Engine games). | Can cause graphical glitches or pop-in as it's technically a "hack". Less common now. |
| **DXVK-GPLAsync** | Modern, more efficient stutter reduction using a proper Vulkan extension. | A more stable alternative to regular Async on supported drivers. | Requires newer drivers that support the `VK_EXT_graphics_pipeline_library` extension. |
| **DXVK-Sarek** | Backports new game fixes to an older DXVK base for maximum compatibility. | **Mali & SD8 Elite users**, Users with older hardware/drivers that don't support modern Vulkan features. | Lacks the latest performance optimizations from the newest official DXVK versions. |

#### Detailed Explanations

-   **Official DXVK:** This is the baseline. When a game needs to show a new visual effect, it has to compile a "shader" for your GPU. This can cause a brief pause or "stutter." Official DXVK does this as needed, so you might see stutter the first time you play through an area.

-   **DXVK-Async:** This is the classic "stutter fix." It moves that shader compilation to a separate, parallel thread. The game doesn't have to wait for it, which makes gameplay feel smoother. However, because the game doesn't wait, a shader might not be ready in time, causing visual glitches like textures popping in late or flickering objects.

-   **DXVK-GPLAsync:** This is the modern successor to Async. It uses an official Vulkan feature (`Graphics Pipeline Library`) that is designed for this exact purpose. It's much more stable and less "hacky" than the original Async, resulting in fewer visual bugs while still reducing stutter. **If your device supports it, this is generally better than the old Async.**

-   **DXVK-Sarek:** Think of this as a Long-Term Support (LTS) version with benefits. It sticks with an older, very compatible DXVK version (like 1.10.3) that works on a wide range of hardware and then adds specific, targeted fixes for newer games. It prioritizes "it runs" over "it runs at the absolute maximum possible FPS." **Suggested for not much supported hardware, such as SD8 Elite & Mali**


#### A Note on Naming Dev Builds
When you convert a Nightly or Dev build (a `.zip` file from GitHub Actions), the filename is usually a long, unhelpful hash like `dxvk-merge-8f0583d9954a...zip`. The script will ask you to provide a meaningful name:

> `Enter DXVK version name (e.g., 2.3-sarek-f1a3b4c):`

Here's how to create a good, informative name:

1.  **Find the Short Hash:** Look at the filename and copy the first 7 characters of the long hash (e.g., `8f0583d`). This is its unique ID.
2.  **Add a Prefix:** Add `master-` or `dev-` at the beginning to indicate it's not an official release.

**Recommended Name Format:** `master-<short_hash>`

**Example:** For the file `dxvk-merge-8f0583d9954a...zip`, a perfect name to enter would be:
**`master-8f0583d`**

This name is short, unique, and allows you to easily find the exact code it was built from on GitHub by searching for the hash.


### Install the `.wcp` files on:

#### Winlator Cmod (Bionic)

1.  Get the latest release of [Winlator Cmod (Bionic)](https://github.com/coffincolors/winlator/releases)
2.  Get the `.wcp` files.
3.  Open Winlator Cmod (Bionic) on your phone.
4.  Navigate to "Contents", and choose which type to install.
5.  Tap the "Install Comntent" button.
6.  Select your `.wcp` file from the file picker. It will be installed soon.
7.  The new component will now be available to select for your containers!


## Credits / Info

The whole code in this repository has been written from scratch, but there's some concepts or infos gathered:
- .wcp general/conversion infos: https://github.com/longjunyu2/winlator/releases, [Convos on the EmuGear International Discord Server](https://discord.com/invite/q842JB4gCm), [r/EmulationOnAndroid](https://www.reddit.com/r/EmulationOnAndroid/), [r/Winlator](https://www.reddit.com/r/Winlator/]
- dxvk conversion core concept inspiration: https://raw.githubusercontent.com/ajay9634/Ajay-prefix/Resources/Termux-scripts/dxvk-wcp.sh, https://raw.githubusercontent.com/ajay9634/Ajay-prefix/Resources/Termux-scripts/dxvk-dev-wcp.sh 
- the documented fexcore winlator fixed workflow (and also inspiration for the one in the project): [TGP-17](https://github.com/FEX-Emu/FEX/compare/main...TGP-17:FEX:ci-test)
