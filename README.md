<div align="center">
  <img src="https://github.com/user-attachments/assets/8102f49b-ef73-496d-81bf-bd19ed398075" alt="icon" width="64" height="64" />
  <h1>TinyClock</h1>
  <p><strong>TinyClock</strong> is a minimalist clock for the Windows system tray.<br>
  The tiniest clock you've ever seen! (so tiny you can barely see it).</p>
  <img src="https://github.com/user-attachments/assets/7ca9fdce-f61f-4f97-b7c4-44f2de2cf599" alt="image" />
</div>

## 🚀 Features
- Displays the time in 12-hour format (without AM/PM)
- Can be configured to automatically start with Windows

## 📦 Installation
1. Download `TinyClock.exe` from [GitHub Releases](https://github.com/Acercandr0/TinyClock/releases).
2. Run `TinyClock.exe`—and you're good to go!

## ⚙️ Optional: Enable TinyClock to start with Windows
Right-click the tray icon and select **"Start with Windows"**.

## 🛠 Build the executable
To build TinyClock successfully, make sure you have Python installed along with the required dependencies.

### 🔹 Install dependencies
Run the following command to install all required Python packages:
```bash
pip install pystray pillow
```
🔹 Generate the .exe
Once the dependencies are installed, run:
```bash
pyinstaller --onefile --windowed --icon=icon.ico TinyClock.py
