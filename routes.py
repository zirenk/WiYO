from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, Poll, Response
from app import app
from functools import wraps
import traceback

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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
        
        # Fetch updated results
        results = get_poll_results(poll_id)
        
        return redirect(url_for('results', poll_id=poll_id, results=results))
    except Exception as e:
        app.logger.error(f"Error in submit_poll: {str(e)}")
        app.logger.error(traceback.format_exc())
        flash('An error occurred while submitting your response. Please try again.', 'error')
        return redirect(url_for('polls'))

@app.route('/results/<int:poll_id>')
@login_required
def results(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    results = request.args.get('results')
    
    if not results:
        results = get_poll_results(poll_id)
    
    return render_template('results.html', poll=poll, poll_data={'question': poll.question, 'results': results})

def get_poll_results(poll_id):
    responses = Response.query.filter_by(poll_id=poll_id).all()
    results = {choice: 0 for choice in Poll.query.get(poll_id).choices}
    for response in responses:
        results[response.choice] += 1
    return results

# Add the rest of the routes here...
