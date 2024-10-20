from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app, db
from models import User, Poll, Response
import random
from sqlalchemy import func
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_code = request.form['login_code']
        logger.info(f"Login attempt with code: {login_code}")
        user = User.query.filter_by(login_code=login_code).first()
        if user:
            session['user_id'] = user.id
            logger.info(f"User {user.username} logged in successfully")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'redirect': url_for('dashboard')})
            return redirect(url_for('dashboard'))
        else:
            logger.info(f"Failed login attempt with code: {login_code}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': 'Invalid login code'})
            flash('Invalid login code', 'danger')
    return render_template('login.html')

@app.route('/create_wiyo_account', methods=['GET', 'POST'])
def create_wiyo_account():
    if request.method == 'POST':
        login_code = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        username = f"Human{random.randint(1000000, 9999999)}"
        
        existing_user = User.query.filter((User.login_code == login_code) | (User.username == username)).first()
        if existing_user:
            flash('An error occurred. Please try again.', 'danger')
            return redirect(url_for('create_wiyo_account'))
        
        new_user = User(login_code=login_code, username=username)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully!', 'success')
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
    
    # Get polls that the user hasn't responded to
    unanswered_polls = Poll.query.filter(
        ~Poll.responses.any((Response.user_id == user_id) & (Response.responded == True))
    ).all()
    
    if unanswered_polls:
        poll = random.choice(unanswered_polls)
        return render_template('polls.html', poll=poll)
    else:
        return render_template('polls.html', no_polls=True)

@app.route('/submit_poll', methods=['POST'])
def submit_poll():
    if 'user_id' not in session:
        flash('Please log in to submit a poll response.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    poll_id = request.form['poll_id']
    choice = request.form['choice']
    
    # Check if the user has already answered this poll
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
        flash('Please log in to view poll results.', 'warning')
        return redirect(url_for('login'))
    poll = Poll.query.get(poll_id)
    if not poll:
        flash('Poll not found.', 'error')
        return redirect(url_for('polls'))
    
    responses = Response.query.filter_by(poll_id=poll_id, responded=True).all()
    
    response_counts = {}
    for choice in poll.choices:
        response_counts[choice] = sum(1 for r in responses if r.choice == choice)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'pollData': response_counts})
    
    return render_template('results.html', poll=poll, responses=responses, poll_data=response_counts)

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
