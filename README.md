# TinyClock ⏳
**TinyClock** is a minimalist clock for the Windows system tray.

## 🚀 Features
- Displays the time in 12-hour format (without AM/PM)
- Can be configured to automatically start with Windows
- Automatic translation based on system language (in testing)

## 📦 Installation
1. Download `TinyClock.exe` from [GitHub Releases](https://github.com/Acercandr0/TinyClock/releases).
2. Run `TinyClock.exe`—and you're good to go!

## ⚙️ Optional: Enable TinyClock to start with Windows
Right-click the tray icon and select **"Start with Windows"**.

## 🛠 Build the executable
To generate your own `.exe`, use:
```bash
pyinstaller --onefile --windowed --icon=icon.ico TinyClock.py
