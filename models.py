from app import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login_code = db.Column(db.String(8), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    demographics = db.Column(JSONB)

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    choices = db.Column(JSONB)
    responses = db.relationship('Response', backref='poll', lazy='dynamic')

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    choice = db.Column(db.String(255), nullable=False)
