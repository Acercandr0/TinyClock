import time
import os
import sys
import gc
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import pystray
import threading
import winreg

class ClockIcon:
    def __init__(self):
        self.icon = pystray.Icon("TinyClock")
        self.running = True
        self.update_thread = threading.Thread(target=self.update_time, daemon=True)

        # Create menu with an auto-start option
        self.icon.menu = pystray.Menu(
            pystray.MenuItem("Start with Windows", self.toggle_startup, checked=lambda _: self.is_registered()),
            pystray.MenuItem("Exit", self.exit_app)
        )

        # Initialize the icon with a valid image
        self.icon.icon = self.create_image()

    def create_image(self):
        """Creates the icon image with the current time, ensuring maximum readability and alignment."""
        width, height = 64, 64  # Optimized resolution for taskbar visibility
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        try:
            font_size_hour = 28  # Balanced size for hour
            font_size_minute = 26  # Slightly smaller to ensure full visibility
            font_hour = ImageFont.truetype("arial.ttf", font_size_hour)
            font_minute = ImageFont.truetype("arial.ttf", font_size_minute)
        except IOError:
            font_hour = ImageFont.load_default()
            font_minute = ImageFont.load_default()

        # Separate hour and minutes
        hour_text = datetime.now().strftime("%I").lstrip('0')
        minute_text = datetime.now().strftime("%M")

        # Get text bounding boxes
        hour_bbox = draw.textbbox((0, 0), hour_text, font=font_hour)
        minute_bbox = draw.textbbox((0, 0), minute_text, font=font_minute)

        hour_width = hour_bbox[2] - hour_bbox[0]
        hour_height = hour_bbox[3] - hour_bbox[1]
        minute_width = minute_bbox[2] - minute_bbox[0]
        minute_height = minute_bbox[3] - minute_bbox[1]

        # Adjust font size dynamically if needed
        while hour_width > width - 8 or minute_width > width - 8:
            font_size_hour -= 2
            font_size_minute -= 2
            try:
                font_hour = ImageFont.truetype("segoeui.ttf", font_size_hour)
                font_minute = ImageFont.truetype("segoeui.ttf", font_size_minute)
            except IOError:
                font_hour = ImageFont.load_default()
                font_minute = ImageFont.load_default()
            hour_bbox = draw.textbbox((0, 0), hour_text, font=font_hour)
            minute_bbox = draw.textbbox((0, 0), minute_text, font=font_minute)
            hour_width = hour_bbox[2] - hour_bbox[0]
            minute_width = minute_bbox[2] - minute_bbox[0]

        # Position hour at the top and minutes lower down, optimizing space
        x_hour = (width - hour_width) // 2
        y_hour = (height // 3) - (hour_height // 3)  # Increased proximity

        x_minute = (width - minute_width) // 2
        y_minute = (2 * height // 3) - (minute_height // 5)  # Adjusted slightly higher

        draw.text((x_hour, y_hour), hour_text, font=font_hour, fill="white")
        draw.text((x_minute, y_minute), minute_text, font=font_minute, fill="white")

        gc.collect()  # Force memory cleanup

        return image

    def update_time(self):
        """Updates the icon every minute while ensuring minimal memory usage."""
        while self.running:
            self.icon.icon = self.create_image()
            self.icon.title = datetime.now().strftime("%I:%M").lstrip('0')  # Consistent title format
            gc.collect()  # Cleanup memory every cycle
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
        gc.collect()  # Cleanup memory on exit

if __name__ == "__main__":
    clock = ClockIcon()
    clock.run()
