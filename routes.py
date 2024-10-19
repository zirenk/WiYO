from flask import render_template, request, redirect, url_for, session, jsonify, flash
from app import app, db
from models import User, Poll, Response
from utils import generate_login_code, generate_username
import random
import logging
from datetime import timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return redirect(url_for('login'))

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
                app.permanent_session_lifetime = timedelta(days=30)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid login code. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/create_wiyo_account', methods=['GET', 'POST'])
def create_wiyo_account():
    if request.method == 'POST':
        try:
            login_code = generate_login_code()
            username = generate_username()
            new_user = User(login_code=login_code, username=username)
            db.session.add(new_user)
            db.session.commit()
            logger.info(f"New user created: {username}")
            return render_template('account_created.html', login_code=login_code, username=username)
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating new user: {str(e)}")
            flash('An error occurred while creating your account. Please try again.', 'danger')
            return render_template('create_wiyo_account.html')
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
        demographics_data = {
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
        user.demographics = demographics_data
        db.session.commit()
        flash('Demographics information updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('demographics.html')

@app.route('/polls')
def polls():
    if 'user_id' not in session:
        flash('Please log in to access polls.', 'warning')
        return redirect(url_for('login'))
    unanswered_polls = Poll.query.filter(
        ~Poll.responses.any(Response.user_id == session['user_id'])
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
    poll_id = request.form['poll_id']
    choice = request.form['choice']
    new_response = Response(user_id=session['user_id'], poll_id=poll_id, choice=choice)
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
    responses = Response.query.filter_by(poll_id=poll_id).all()
    return render_template('results.html', poll=poll, responses=responses)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))
