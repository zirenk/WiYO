import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, Poll, Response
from sqlalchemy import and_, cast, Integer
from app import app
from utils import generate_login_code, generate_username
from functools import wraps
import traceback
import openai

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

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
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

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user_id' not in session:
        flash('Please log in to access the chat feature.', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user_message = request.form['user_message']
        
        # Initialize OpenAI API
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        
        try:
            # Include user demographics in the context
            user_context = f"User demographics: {user.demographics}"
            
            # Generate AI response
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are WiYO AI, a helpful assistant for the anonymous polling application. {user_context}"},
                    {"role": "user", "content": user_message}
                ]
            )
            
            ai_message = response.choices[0].message['content']
            
            return jsonify({"ai_message": ai_message})
        
        except openai.error.OpenAIError as e:
            app.logger.error(f"OpenAI API error: {str(e)}")
            return jsonify({"error": "An error occurred while processing your request. Please try again later."}), 503
        
        except Exception as e:
            app.logger.error(f"Unexpected error in chat route: {str(e)}")
            return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500
    
    return render_template('chat.html', username=user.username)

# Add other routes (polls, demographics, etc.) here
