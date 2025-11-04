# Expense Tracker App

A simple expense tracker application built with Kivy and KivyMD that can be compiled to an Android APK using Buildozer.

## Features

- Add expenses with amount, category, and optional notes
- View all expenses in a list
- Calculate and display total expenses
- Data persistence using TinyDB

## Installation

1. Install Python 3.11 (or 3.10)
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

To run the application on desktop:
```
python main.py
```

## Building for Android

This application is designed to be built into an Android APK using Buildozer on WSL (Windows Subsystem for Linux).

### Prerequisites

1. Install WSL with Ubuntu:
   ```
   wsl --install
   ```

2. In your Ubuntu terminal, update the system:
   ```
   sudo apt update && sudo apt upgrade -y
   ```

3. Install required dependencies:
   ```
   sudo apt install python3-pip build-essential git python3-dev ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev -y
   ```

4. Install Buildozer:
   ```
   pip install --user buildozer
   ```

5. Install additional Android SDK/NDK tools:
   ```
   sudo apt install openjdk-17-jdk -y
   ```

### Building the APK

1. Navigate to your project folder in WSL:
   ```
   cd /mnt/c/Users/YourName/Desktop/exp
   ```

2. Initialize Buildozer (if not already done):
   ```
   buildozer init
   ```

3. Build the APK:
   ```
   buildozer -v android debug
   ```

The first build will take 10-30 minutes as it downloads the Android SDK, NDK, and Python for Android.

The APK will be located in the `bin/` folder: `bin/expense_tracker-1.0-debug.apk`

## Continuous Integration (optional)

A GitHub Actions workflow is included to build the APK in CI. Push to the `main` branch or run the workflow manually to start a build on GitHub-hosted runners. The workflow will attempt to install system packages, run Buildozer and upload the resulting APK as an artifact.

Notes:
- CI builds are long-running (first run downloads Android SDK/NDK and toolchains) and may require a runner timeout increase.
- The workflow file is `.github/workflows/build-apk.yml` in the repository.

CI trigger: this file was edited automatically to trigger a CI build for the Android APK.

### Installing the APK

You can install the APK on your Android device by:

1. Copying it to your phone and opening it, or
2. Using ADB:
   ```
   adb install bin/expense_tracker-1.0-debug.apk
   ```

## License

This project is open source and available under the MIT License.