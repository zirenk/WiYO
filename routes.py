from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, Poll, Response
from app import app
from functools import wraps
import traceback

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

        response = Response(user_id=user.id, poll_id=poll_id, choice=choice)
        db.session.add(response)
        db.session.commit()

        flash('Your response has been recorded. View the results below.', 'success')

        return redirect(url_for('results', poll_id=poll_id))
    except Exception as e:
        app.logger.error(f"Error in submit_poll: {str(e)}")
        app.logger.error(traceback.format_exc())
        flash('An error occurred while submitting your response. Please try again.', 'error')
        return redirect(url_for('polls'))

@app.route('/results/<int:poll_id>', methods=['GET', 'POST'])
@login_required
def results(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    results = get_poll_results(poll_id)

    if request.method == 'POST':
        age = request.form.get('age')
        gender = request.form.get('gender')
        education = request.form.get('education')
        
        filtered_results = apply_demographic_filters(results, age, gender, education)
        
        return jsonify({
            'poll_data': {
                'question': poll.question,
                'results': filtered_results
            }
        })

    return render_template('results.html',
                           poll=poll,
                           poll_data={
                               'question': poll.question,
                               'results': results
                           })

def get_poll_results(poll_id):
    responses = Response.query.filter_by(poll_id=poll_id).all()
    results = {choice: 0 for choice in Poll.query.get(poll_id).choices}
    for response in responses:
        results[response.choice] += 1
    return results

def apply_demographic_filters(results, age, gender, education):
    return results

@app.route('/create_wiyo_account', methods=['GET', 'POST'])
def create_wiyo_account():
    pass

@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Server Error: {str(e)}")
    app.logger.error(traceback.format_exc())
    return "Internal Server Error", 500