from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Candidate(db.Model):
    __tablename__ = 'candidates'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    kelas = db.Column(db.String(50))
    foto = db.Column(db.Text)

class Token(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.Boolean, default=False)
    waktu_pakai = db.Column(db.DateTime)

class Vote(db.Model):
    __tablename__ = 'votes'
    id = db.Column(db.Integer, primary_key=True)
    token_id = db.Column(db.Integer, db.ForeignKey('tokens.id'))
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'))
    waktu_vote = db.Column(db.DateTime, default=datetime.utcnow)
