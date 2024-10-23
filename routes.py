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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_code = request.form.get('login_code')
        remember_me = bool(request.form.get('remember_me'))
        
        logger.debug(f"Login attempt with code length: {len(login_code) if login_code else 'None'}")
        
        user = User.query.filter_by(login_code=login_code).first()
        logger.debug(f"User found: {user is not None}")
        
        if user:
            login_user(user, remember=remember_me)
            session['user_id'] = user.id
            logger.debug(f"User logged in successfully. Session ID: {user.id}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'redirect': url_for('dashboard')})
            return redirect(url_for('dashboard'))
        else:
            logger.warning(f"Failed login attempt with code: {login_code}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': 'Invalid login code'})
            flash('Invalid login code', 'danger')
            
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/polls')
@login_required
def polls():
    # Get first unanswered poll for the user
    responded_polls = Response.query.filter_by(user_id=current_user.id).with_entities(Response.poll_id).all()
    responded_poll_ids = [p[0] for p in responded_polls]
    
    next_poll = Poll.query.filter(~Poll.id.in_(responded_poll_ids)).order_by(Poll.number).first()
    
    if next_poll is None:
        return render_template('polls.html', no_polls=True)
    
    return render_template('polls.html', poll=next_poll, no_polls=False)

@app.route('/forum')
@login_required
def forum():
    forums = ForumPost.query.order_by(ForumPost.date_posted.desc()).all()
    return render_template('forum.html', forums=forums)

@app.route('/forum/<int:forum_id>')
@login_required
def forum_details(forum_id):
    forum = ForumPost.query.get_or_404(forum_id)
    comments = Comment.query.filter_by(forum_post_id=forum_id).order_by(Comment.date_posted.desc()).all()
    return render_template('forum_details.html', forum=forum, comments=comments)

@app.route('/demographics', methods=['GET', 'POST'])
@login_required
def demographics():
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = request.get_json()
            current_user.demographics = data
            db.session.commit()
            return jsonify({'success': True})
        return redirect(url_for('demographics'))
    
    return render_template('demographics.html', user=current_user, edit_mode=False)

@app.route('/create_wiyo_account', methods=['GET', 'POST'])
def create_wiyo_account():
    if request.method == 'POST':
        try:
            login_code = generate_login_code()
            username = generate_username()
            logger.debug(f"Creating new account with username: {username}")
            
            new_user = User(login_code=login_code, username=username)
            db.session.add(new_user)
            db.session.commit()
            logger.debug(f"Account created successfully for username: {username}")
            
            flash('Your WiYO account has been created successfully!', 'success')
            return render_template('account_created.html', login_code=login_code, username=username)
        except Exception as e:
            logger.error(f"Error creating account: {str(e)}")
            db.session.rollback()
            flash('Error creating account: ' + str(e), 'danger')
            return redirect(url_for('create_wiyo_account'))
    
    return render_template('create_wiyo_account.html')
