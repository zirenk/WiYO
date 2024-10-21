import os
from app import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login_code = db.Column(db.String(8), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    demographics = db.Column(JSONB)
    forum_posts = db.relationship('ForumPost', backref='author', lazy='dynamic')

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    question = db.Column(db.String(255), nullable=False)
    choices = db.Column(JSONB)
    responses = db.relationship('Response', backref='poll', lazy='dynamic')

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    choice = db.Column(db.String(255), nullable=False)
    responded = db.Column(db.Boolean, default=True, nullable=False)

    user = db.relationship('User', backref=db.backref('responses', lazy='dynamic'))

class ForumPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
