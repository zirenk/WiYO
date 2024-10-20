from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from app import app, db
from models import User, Poll, Response
from sqlalchemy import and_, cast, Integer
from utils import generate_login_code, generate_username
from functools import wraps
import traceback

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    
    total_polls = Poll.query.count()
    polls_answered = Response.query.filter_by(user_id=user.id, responded=True).count()
    polls_remaining = total_polls - polls_answered
    progress = int((polls_answered / total_polls) * 100) if total_polls > 0 else 0
    
    return render_template('dashboard.html', 
                           username=user.username,
                           total_polls=total_polls,
                           polls_answered=polls_answered,
                           polls_remaining=polls_remaining,
                           progress=progress)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_code = request.form.get('login_code')
        remember_me = 'remember_me' in request.form
        
        user = User.query.filter_by(login_code=login_code).first()
        if user:
            session['user_id'] = user.id
            if remember_me:
                session.permanent = True
            flash('Logged in successfully!', 'success')
            return jsonify({"success": True, "redirect": url_for('dashboard')})
        else:
            return jsonify({"success": False, "error": "Invalid login code. Please try again."})
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/create_wiyo_account', methods=['GET', 'POST'])
def create_wiyo_account():
    if request.method == 'POST':
        login_code = generate_login_code()
        username = generate_username()
        
        new_user = User(login_code=login_code, username=username)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Your WiYO account has been created successfully!', 'success')
        return render_template('account_created.html', login_code=login_code, username=username)
    
    return render_template('create_wiyo_account.html')

# Add other routes as needed
