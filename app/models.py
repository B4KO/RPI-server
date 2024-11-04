# app/models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Humidity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    humidity = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.String(100), nullable=False)

class Temperature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.String(100), nullable=False)

class Pressure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pressure = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.String(100), nullable=False)
