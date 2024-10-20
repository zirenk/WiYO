import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, Poll, Response
from sqlalchemy import and_, cast, Integer
from app import app
from utils import generate_login_code, generate_username
from functools import wraps
import traceback
from openai import OpenAI
from openai import APIError, RateLimitError
import time
import random
from queue import Queue
import threading

# Create a queue for handling API requests
api_request_queue = Queue()

# Function to process API requests from the queue
def process_api_requests():
    while True:
        user_id, user_message = api_request_queue.get()
        try:
            response = make_openai_request(user_id, user_message)
            # Store the response or notify the user
        except Exception as e:
            # Handle errors
            pass
        api_request_queue.task_done()

# Start the background thread for processing API requests
api_thread = threading.Thread(target=process_api_requests, daemon=True)
api_thread.start()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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
            return jsonify({"success": True, "redirect": url_for('dashboard')})
        else:
            return jsonify({"success": False, "error": "Invalid login code. Please try again."})
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', username=user.username)

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

@app.route('/demographics', methods=['GET', 'POST'])
@login_required
def demographics():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
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
        return redirect(url_for('dashboard'))
    return render_template('demographics.html', user=user, edit_mode=True)

def make_openai_request(user_id, user_message, max_retries=5, base_delay=1):
    user = User.query.get(user_id)
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    for attempt in range(max_retries):
        try:
            user_context = f"User demographics: {user.demographics}"
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are WiYO AI, a helpful assistant for the anonymous polling application. {user_context}"},
                    {"role": "user", "content": user_message}
                ]
            )
            
            return response.choices[0].message.content
        
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
        
        except APIError as e:
            app.logger.error(f"OpenAI API error: {str(e)}")
            raise
        
        except Exception as e:
            app.logger.error(f"Unexpected error in chat route: {str(e)}")
            raise

@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user_message = request.form['user_message']
        
        try:
            # Add the request to the queue
            api_request_queue.put((user.id, user_message))
            
            return jsonify({
                "status": "queued",
                "message": "Your request has been queued. Please wait for the response."
            })
        
        except Exception as e:
            app.logger.error(f"Unexpected error in chat route: {str(e)}")
            return jsonify({
                "error": "An unexpected error occurred. Please try again later.",
                "details": str(e)
            }), 500
    
    return render_template('chat.html', username=user.username)

@app.route('/chat/status', methods=['GET'])
@login_required
def chat_status():
    user = User.query.get(session['user_id'])
    # Check if there's a response ready for this user
    # This is a placeholder - you'll need to implement a way to store and retrieve responses
    response_ready = False
    ai_message = None
    
    if response_ready:
        return jsonify({
            "status": "complete",
            "ai_message": ai_message
        })
    else:
        return jsonify({
            "status": "pending",
            "message": "Your request is still being processed. Please wait."
        })

@app.route('/polls')
@login_required
def polls():
    user = User.query.get(session['user_id'])
    unanswered_polls = Poll.query.outerjoin(Response, and_(Response.poll_id == Poll.id, Response.user_id == user.id)).filter(Response.id == None).order_by(Poll.number).first()

    if unanswered_polls:
        return render_template('polls.html', poll=unanswered_polls)
    else:
        return render_template('polls.html', no_polls=True)

@app.route('/submit_poll', methods=['POST'])
@login_required
def submit_poll():
    user = User.query.get(session['user_id'])
    poll_id = request.form['poll_id']
    choice = request.form['choice']

    response = Response(user_id=user.id, poll_id=poll_id, choice=choice)
    db.session.add(response)
    db.session.commit()

    flash('Your response has been recorded.', 'success')
    return redirect(url_for('polls'))

@app.route('/results/<int:poll_id>')
@login_required
def results(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    responses = Response.query.filter_by(poll_id=poll_id).all()
    
    results = {choice: 0 for choice in poll.choices}
    for response in responses:
        results[response.choice] += 1

    return render_template('results.html', poll=poll, results=results)

@app.route('/reset_responses')
@login_required
def reset_responses():
    user = User.query.get(session['user_id'])
    Response.query.filter_by(user_id=user.id).delete()
    db.session.commit()
    flash('Your responses have been reset. You can now answer the polls again.', 'success')
    return redirect(url_for('polls'))
