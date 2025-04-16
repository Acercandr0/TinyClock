import time
import os
import sys
import locale  # Detectar idioma del sistema
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

        # Obtener idioma del sistema y traducir opciones
        self.lang = locale.getdefaultlocale()[0][:2]  # Extrae código de idioma (ej: 'es', 'en', 'fr')
        self.texts = self.get_translations()

        # Crear menú con opción de inicio automático
        self.icon.menu = pystray.Menu(
            pystray.MenuItem(self.texts["startup"], self.toggle_startup, checked=lambda _: self.is_registered()),
            pystray.MenuItem(self.texts["exit"], self.exit_app)
        )

    def get_translations(self):
        """Devuelve los textos traducidos según el idioma del sistema."""
        translations = {
            "en": {"startup": "Start with Windows", "exit": "Exit"},
            "es": {"startup": "Iniciar con Windows", "exit": "Salir"},
            "fr": {"startup": "Démarrer avec Windows", "exit": "Quitter"},
            "de": {"startup": "Mit Windows starten", "exit": "Beenden"}
        }
        return translations.get(self.lang, translations["en"])  # Usa inglés como predeterminado si no hay traducción

    def create_image(self):
        """Crea la imagen del icono con la hora actual."""
        width, height = 128, 128
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        try:
            font_size = 60
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        time_text = datetime.now().strftime("%I:%M").lstrip('0')

        bbox = draw.textbbox((0, 0), time_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (width - text_width) // 2
        y = (height - text_height) // 2

        draw.text((x, y), time_text, font=font, fill="white")

        return image

    def update_time(self):
        """Actualiza el icono cada minuto."""
        while self.running:
            self.icon.icon = self.create_image()
            self.icon.title = datetime.now().strftime("%I:%M %p").lstrip('0')
            time.sleep(60 - datetime.now().second)

    def toggle_startup(self):
        """Activa o desactiva el inicio automático en Windows."""
        clave_registro = r"Software\Microsoft\Windows\CurrentVersion\Run"
        nombre_programa = "TinyClock"
        ruta_exe = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)

        if self.is_registered():
            # Eliminar TinyClock del inicio
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, clave_registro, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, nombre_programa)
                print("TinyClock se ha eliminado del inicio automático.")
            except Exception as e:
                print(f"No se pudo eliminar TinyClock del inicio: {e}")
        else:
            # Registrar TinyClock en el inicio
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, clave_registro, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, nombre_programa, 0, winreg.REG_SZ, ruta_exe)
                print("TinyClock ahora se ejecutará al inicio de Windows.")
            except Exception as e:
                print(f"No se pudo registrar TinyClock en el inicio: {e}")

    def is_registered(self):
        """Verifica si TinyClock está registrado para iniciarse con Windows."""
        clave_registro = r"Software\Microsoft\Windows\CurrentVersion\Run"
        nombre_programa = "TinyClock"

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, clave_registro, 0, winreg.KEY_READ) as key:
                winreg.QueryValueEx(key, nombre_programa)
            return True
        except FileNotFoundError:
            return False

    def run(self):
        """Ejecuta TinyClock en la bandeja del sistema."""
        self.update_thread.start()
        self.icon.run()

    def exit_app(self):
        """Cierra la aplicación."""
        self.running = False
        self.icon.stop()

if __name__ == "__main__":
    clock = ClockIcon()
    clock.run()