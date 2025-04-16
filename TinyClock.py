import time
import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import pystray
import threading
import winreg

class ClockIcon:
    def __init__(self):
        self.icon = pystray.Icon("TinyClock")
        self.running = True
        self.update_thread = threading.Thread(target=self.update_time)
        self.update_thread.daemon = True

        # Create menu with an auto-start option
        self.icon.menu = pystray.Menu(
            pystray.MenuItem("Start with Windows", self.toggle_startup, checked=lambda _: self.is_registered()),
            pystray.MenuItem("Exit", self.exit_app)
        )

        # Initialize the icon with a valid image
        self.icon.icon = self.create_image()

    def create_image(self):
        """Creates the icon image with the current time, ensuring legibility."""
        width, height = 128, 128
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        try:
            font_size = 60
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        # Format time without AM/PM
        time_text = datetime.now().strftime("%I:%M").lstrip('0')

        # Get text bounding box to ensure all digits are visible
        bbox = draw.textbbox((0, 0), time_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Adjust font size dynamically if needed
        while text_width > width - 10:
            font_size -= 2
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), time_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

        x = (width - text_width) // 2
        y = (height - text_height) // 2

        draw.text((x, y), time_text, font=font, fill="white")

        return image

    def update_time(self):
        """Updates the icon every minute."""
        while self.running:
            self.icon.icon = self.create_image()
            self.icon.title = datetime.now().strftime("%I:%M").lstrip('0')  # Keep format without AM/PM
            time.sleep(60 - datetime.now().second)

    def toggle_startup(self):
        """Enables or disables automatic startup in Windows."""
        registry_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "TinyClock"
        exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)

        if self.is_registered():
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, app_name)
                print("TinyClock removed from startup.")
            except Exception as e:
                print(f"Could not remove TinyClock from startup: {e}")
        else:
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
                print("TinyClock will now start with Windows.")
            except Exception as e:
                print(f"Could not set TinyClock to start with Windows: {e}")

    def is_registered(self):
        """Checks if TinyClock is registered for startup in Windows."""
        registry_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "TinyClock"

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key, 0, winreg.KEY_READ) as key:
                winreg.QueryValueEx(key, app_name)
            return True
        except FileNotFoundError:
            return False

    def run(self):
        """Runs TinyClock in the system tray."""
        self.update_thread.start()
        self.icon.run()

    def exit_app(self):
        """Closes the application."""
        self.running = False
        self.icon.stop()

if __name__ == "__main__":
    clock = ClockIcon()
    clock.run()
