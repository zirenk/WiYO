import os
import random
import string
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, Poll, Response
from sqlalchemy import and_, cast, Integer
from app import app
from utils import generate_login_code, generate_username
from functools import wraps

def generate_timestamp():
    return int(datetime.utcnow().timestamp())

@app.context_processor
def inject_timestamp():
    return dict(timestamp=generate_timestamp())

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_code = request.form['login_code']
        user = User.query.filter_by(login_code=login_code).first()
        if user:
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid login code. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/create_wiyo_account', methods=['GET', 'POST'])
def create_wiyo_account():
    if request.method == 'POST':
        login_code = generate_login_code()
        username = generate_username()
        new_user = User(login_code=login_code, username=username)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please save your login code.', 'success')
        return render_template('account_created.html', login_code=login_code, username=username)
    return render_template('create_wiyo_account.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', username=user.username)

@app.route('/demographics', methods=['GET', 'POST'])
def demographics():
    if 'user_id' not in session:
        flash('Please log in to access demographics.', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        if 'edit_demographics' in request.form:
            return render_template('demographics.html', user=user, edit_mode=True)
        else:
            user.demographics = {
                'age': request.form['age'],
                'gender': request.form['gender'],
                'education': request.form['education'],
                'employment': request.form['employment'],
                'marital_status': request.form['marital_status'],
                'income': request.form['income'],
                'location': request.form['location'],
                'ethnicity': request.form['ethnicity'],
                'political_affiliation': request.form['political_affiliation'],
                'religion': request.form['religion']
            }
            db.session.commit()
            flash('Demographics updated successfully!', 'success')
            return redirect(url_for('demographics'))
    
    return render_template('demographics.html', user=user, edit_mode=False)

@app.route('/polls')
def polls():
    if 'user_id' not in session:
        flash('Please log in to access polls.', 'warning')
        return redirect(url_for('login'))
    user_id = session['user_id']
    
    unanswered_polls = Poll.query.filter(
        ~Poll.responses.any((Response.user_id == user_id) & (Response.responded == True))
    ).all()
    
    if unanswered_polls:
        poll = random.choice(unanswered_polls)
        return render_template('polls.html', poll=poll)
    else:
        flash('You have answered all available polls. Check back later for new ones!', 'info')
        return render_template('polls.html', no_polls=True)

@app.route('/submit_poll', methods=['POST'])
def submit_poll():
    if 'user_id' not in session:
        flash('Please log in to submit a poll response.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    poll_id = request.form['poll_id']
    choice = request.form['choice']
    
    existing_response = Response.query.filter_by(user_id=user_id, poll_id=poll_id, responded=True).first()
    if existing_response:
        flash('You have already answered this poll.', 'warning')
        return redirect(url_for('polls'))
    
    new_response = Response(user_id=user_id, poll_id=poll_id, choice=choice, responded=True)
    db.session.add(new_response)
    db.session.commit()
    flash('Poll response submitted successfully!', 'success')
    return redirect(url_for('results', poll_id=poll_id))

@app.route('/results/<int:poll_id>')
def results(poll_id):
    if 'user_id' not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Please log in to view poll results.'}), 401
        flash('Please log in to view poll results.', 'warning')
        return redirect(url_for('login'))
    
    poll = Poll.query.get(poll_id)
    if not poll:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Poll not found.'}), 404
        flash('Poll not found.', 'error')
        return redirect(url_for('polls'))
    
    try:
        # Get demographic filters from request
        age = request.args.get('age')
        gender = request.args.get('gender')
        education = request.args.get('education')
        
        # Base query
        query = Response.query.filter_by(poll_id=poll_id, responded=True)
        
        # Apply demographic filters
        if age:
            age_range = age.split('-')
            if len(age_range) == 2:
                min_age, max_age = int(age_range[0]), int(age_range[1])
                query = query.join(User).filter(
                    and_(
                        cast(User.demographics['age'].astext, Integer) >= min_age,
                        cast(User.demographics['age'].astext, Integer) <= max_age
                    )
                )
            elif age == '55+':
                query = query.join(User).filter(cast(User.demographics['age'].astext, Integer) >= 55)
        if gender:
            query = query.join(User).filter(User.demographics['gender'].astext == gender)
        if education:
            query = query.join(User).filter(User.demographics['education'].astext == education)
        
        responses = query.all()
        
        response_counts = {}
        for choice in poll.choices:
            response_counts[choice] = sum(1 for r in responses if r.choice == choice)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'pollData': response_counts})
        
        return render_template('results.html', poll=poll, responses=responses, poll_data=response_counts)
    
    except Exception as e:
        app.logger.error(f"Error in results route: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'An error occurred while fetching poll data.'}), 500
        flash('An error occurred while fetching poll data.', 'error')
        return redirect(url_for('polls'))

@app.route('/reset_responses')
def reset_responses():
    if 'user_id' not in session:
        flash('Please log in to reset responses.', 'warning')
        return redirect(url_for('login'))
    user_id = session['user_id']
    Response.query.filter_by(user_id=user_id).update({Response.responded: False})
    db.session.commit()
    flash('Your poll responses have been reset. You can now answer polls again.', 'success')
    return redirect(url_for('polls'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))