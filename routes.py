from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, Poll, Response, ForumPost, Comment
from app import app
from functools import wraps
import traceback
from utils import generate_login_code, generate_username

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_code = request.form.get('login_code')
        user = User.query.filter_by(login_code=login_code).first()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if user:
                session['user_id'] = user.id
                return jsonify({'success': True, 'redirect': url_for('dashboard')})
            else:
                return jsonify({'success': False, 'error': 'Invalid login code. Please try again.'})
        else:
            if user:
                session['user_id'] = user.id
                flash('Login successful!', 'success')
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
        
        flash('Your WiYO account has been created successfully!', 'success')
        return render_template('account_created.html', login_code=login_code, username=username)
    
    return render_template('create_wiyo_account.html')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', username=user.username)

@app.route('/submit_poll', methods=['POST'])
@login_required
def submit_poll():
    try:
        user = User.query.get(session['user_id'])
        poll_id = request.form['poll_id']
        choice = request.form['choice']

        poll = Poll.query.get_or_404(poll_id)

        if choice not in poll.choices:
            flash('Invalid choice selected. Please try again.', 'error')
            return redirect(url_for('polls'))

        existing_response = Response.query.filter_by(user_id=user.id, poll_id=poll_id).first()
        if existing_response:
            existing_response.choice = choice
        else:
            response = Response(user_id=user.id, poll_id=poll_id, choice=choice)
            db.session.add(response)

        db.session.commit()

        flash('Your response has been recorded. View the results below.', 'success')

        # Redirect to results page immediately after submission
        return redirect(url_for('results', poll_id=poll_id, just_submitted=True))
    except Exception as e:
        app.logger.error(f"Error in submit_poll: {str(e)}")
        app.logger.error(traceback.format_exc())
        flash('An error occurred while submitting your response. Please try again.', 'error')
        return redirect(url_for('polls'))

@app.route('/results/<int:poll_id>')
@login_required
def results(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    results = get_poll_results(poll_id)
    just_submitted = request.args.get('just_submitted', type=bool, default=False)

    return render_template('results.html',
                           poll=poll,
                           poll_data={
                               'question': poll.question,
                               'results': results
                           },
                           just_submitted=just_submitted)

def get_poll_results(poll_id):
    poll = Poll.query.get(poll_id)
    if not poll:
        return {}

    results = {choice: 0 for choice in poll.choices}
    responses = Response.query.filter_by(poll_id=poll_id).all()
    for response in responses:
        results[response.choice] += 1
    return results

@app.route('/polls')
@login_required
def polls():
    user = User.query.get(session['user_id'])
    unanswered_polls = Poll.query.filter(
        ~Poll.responses.any(Response.user_id == user.id)
    ).order_by(Poll.number).all()

    if not unanswered_polls:
        return render_template('polls.html', no_polls=True)

    next_poll = unanswered_polls[0]
    return render_template('polls.html', poll=next_poll)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))
