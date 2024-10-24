from flask import (
    render_template, request, redirect, url_for, flash, 
    jsonify, session
)
from flask_login import (
    LoginManager, login_user, logout_user, 
    login_required, current_user
)
from app import app, db, login_manager
from models import User, Poll, Response, ForumPost, Comment
from utils import generate_login_code, generate_username
import json
import openai
import os
import time
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/submit_poll', methods=['POST'])
@login_required
def submit_poll():
    poll_id = request.form.get('poll_id')
    choice = request.form.get('choice')
    
    if not poll_id or not choice:
        flash('Invalid submission', 'error')
        return redirect(url_for('polls'))
        
    poll = Poll.query.get_or_404(poll_id)
    
    # Check if user has already responded to this poll
    existing_response = Response.query.filter_by(
        user_id=current_user.id,
        poll_id=poll_id
    ).first()
    
    if existing_response:
        flash('You have already responded to this poll', 'error')
        return redirect(url_for('polls'))
        
    # Create new response
    response = Response(
        user_id=current_user.id,
        poll_id=poll_id,
        choice=choice
    )
    db.session.add(response)
    db.session.commit()
    
    return redirect(url_for('results', poll_id=poll_id, just_submitted=True))
