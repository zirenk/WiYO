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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_code = request.form.get('login_code')
        remember_me = bool(request.form.get('remember_me'))
        
        user = User.query.filter_by(login_code=login_code).first()
        
        if user:
            login_user(user, remember=remember_me)
            session['user_id'] = user.id
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'redirect': url_for('dashboard')})
            return redirect(url_for('dashboard'))
        else:
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

@app.route('/chat', methods=['GET'])
@login_required
def chat():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
@login_required
def process_chat():
    if not request.is_json:
        return jsonify({'error': 'Invalid request format'}), 400
    
    user_message = request.json.get('user_message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
        # Create a chat completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are WiYO AI, a helpful assistant focused on providing clear and concise responses."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        # Extract the AI's response
        ai_message = response.choices[0].message.content.strip()
        return jsonify({'ai_message': ai_message})
    
    except openai.RateLimitError:
        return jsonify({'error': 'Rate limit exceeded. Please try again in a moment.'}), 429
    except openai.AuthenticationError:
        return jsonify({'error': 'Authentication error with OpenAI API.'}), 401
    except Exception as e:
        app.logger.error(f"Error in chat: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request.'}), 500

@app.route('/chat/status', methods=['GET'])
@login_required
def chat_status():
    return jsonify({'status': 'complete', 'message': 'Direct response mode is active'})

# Re-add other existing routes
@app.route('/create_wiyo_account', methods=['GET', 'POST'])
def create_wiyo_account():
    if request.method == 'POST':
        try:
            login_code = generate_login_code()
            username = generate_username()
            
            new_user = User(login_code=login_code, username=username)
            db.session.add(new_user)
            db.session.commit()
            
            flash('Your WiYO account has been created successfully!', 'success')
            return render_template('account_created.html', login_code=login_code, username=username)
        except Exception as e:
            db.session.rollback()
            flash('Error creating account: ' + str(e), 'danger')
            return redirect(url_for('create_wiyo_account'))
    
    return render_template('create_wiyo_account.html')

# Include all other existing routes...
