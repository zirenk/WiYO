import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, Poll, Response, ForumPost, Comment
from sqlalchemy import and_, cast, Integer, desc
from app import app
from utils import generate_login_code, generate_username
from functools import wraps
import traceback
from openai import OpenAI
from openai import APIError, RateLimitError, AuthenticationError
import time
import random
from queue import Queue
import threading

api_request_queue = Queue()
user_responses = {}

def process_api_requests():
    while True:
        user_id, user_message = api_request_queue.get()
        try:
            app.logger.info(f"Processing request for user {user_id}")
            with app.app_context():
                response = make_openai_request(user_id, user_message)
                user_responses[user_id] = response
                app.logger.info(f"Response stored for user {user_id}: {response[:50]}...")
        except Exception as e:
            app.logger.error(f"Error processing request for user {user_id}: {str(e)}")
            app.logger.error(traceback.format_exc())
        finally:
            api_request_queue.task_done()

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
    
    models_to_try = ["gpt-3.5-turbo", "gpt-3.5-turbo-instruct", "text-davinci-002", "davinci"]
    
    for model in models_to_try:
        for attempt in range(max_retries):
            try:
                user_context = f"User demographics: {user.demographics}"
                
                app.logger.info(f"Sending request to OpenAI API for user {user_id} using model {model}")
                if model.startswith("gpt-3.5-turbo"):
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": f"You are WiYO AI, a helpful assistant for the anonymous polling application. {user_context}"},
                            {"role": "user", "content": user_message}
                        ],
                        max_tokens=150
                    )
                    ai_message = response.choices[0].message.content
                else:
                    response = client.completions.create(
                        model=model,
                        prompt=f"WiYO AI is a helpful assistant for the anonymous polling application. {user_context}\nUser: {user_message}\nWiYO AI:",
                        max_tokens=150
                    )
                    ai_message = response.choices[0].text.strip()
                
                app.logger.info(f"Received response from OpenAI API for user {user_id}")
                return ai_message
            
            except AuthenticationError as e:
                app.logger.error(f"Authentication error for user {user_id}: {str(e)}")
                raise
            
            except RateLimitError:
                if attempt == max_retries - 1:
                    app.logger.error(f"Rate limit exceeded for user {user_id} after {max_retries} attempts")
                    raise
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                app.logger.warning(f"Rate limit hit for user {user_id}. Retrying in {delay:.2f} seconds")
                time.sleep(delay)
            
            except APIError as e:
                if "does not have access to model" in str(e):
                    app.logger.warning(f"No access to model {model} for user {user_id}. Trying next model.")
                    break
                if attempt == max_retries - 1:
                    app.logger.error(f"API error for user {user_id}: {str(e)}")
                    raise
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                app.logger.warning(f"API error for user {user_id}. Retrying in {delay:.2f} seconds")
                time.sleep(delay)
            
            except Exception as e:
                app.logger.error(f"Unexpected error in make_openai_request for user {user_id}: {str(e)}")
                app.logger.error(traceback.format_exc())
                if attempt == max_retries - 1:
                    raise
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                app.logger.warning(f"Unexpected error for user {user_id}. Retrying in {delay:.2f} seconds")
                time.sleep(delay)
    
    raise Exception("All models attempted. Unable to get a response from OpenAI API.")

@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user_message = request.json['user_message']
        
        try:
            api_request_queue.put((user.id, user_message))
            app.logger.info(f"Request queued for user {user.id}")
            
            return jsonify({
                "status": "queued",
                "message": "Your request has been queued. Please wait for the response."
            })
        
        except Exception as e:
            app.logger.error(f"Unexpected error in chat route for user {user.id}: {str(e)}")
            app.logger.error(traceback.format_exc())
            return jsonify({
                "error": "An unexpected error occurred. Please try again later.",
                "details": str(e)
            }), 500
    
    return render_template('chat.html', username=user.username)

@app.route('/chat/status', methods=['GET'])
@login_required
def chat_status():
    user = User.query.get(session['user_id'])
    
    if user.id in user_responses:
        ai_message = user_responses.pop(user.id)
        app.logger.info(f"Response retrieved for user {user.id}: {ai_message[:50]}...")
        return jsonify({
            "status": "complete",
            "ai_message": ai_message
        })
    else:
        app.logger.info(f"No response available yet for user {user.id}")
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

    poll = Poll.query.get_or_404(poll_id)

    if choice not in poll.choices:
        flash('Invalid choice selected. Please try again.', 'error')
        return redirect(url_for('polls'))

    response = Response(user_id=user.id, poll_id=poll_id, choice=choice)
    db.session.add(response)
    db.session.commit()

    flash('Your response has been recorded.', 'success')
    
    return redirect(url_for('results', poll_id=poll_id))

@app.route('/results/<int:poll_id>')
@login_required
def results(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    
    age_filter = request.args.get('age', 'All')
    gender_filter = request.args.get('gender', 'All')
    education_filter = request.args.get('education', 'All')

    responses_query = Response.query.filter_by(poll_id=poll_id)

    if age_filter != 'All':
        age_range = age_filter.split('-')
        responses_query = responses_query.join(User).filter(
            cast(User.demographics['age'].astext, Integer).between(int(age_range[0]), int(age_range[1]))
        )

    if gender_filter != 'All':
        responses_query = responses_query.join(User).filter(User.demographics['gender'].astext == gender_filter)

    if education_filter != 'All':
        responses_query = responses_query.join(User).filter(User.demographics['education'].astext == education_filter)

    responses = responses_query.all()

    if not responses:
        no_data_message = 'There are no responses based on your filter. Please edit some filters and try again.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'no_data': True, 'message': no_data_message})
        else:
            flash(no_data_message, 'info')
            return render_template('results.html', poll=poll, no_data=True)

    results = {choice: 0 for choice in poll.choices}
    for response in responses:
        results[response.choice] += 1

    poll_data = {
        'question': poll.question,
        'results': results
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'poll_data': poll_data})
    else:
        return render_template('results.html', poll=poll, results=results, poll_data=poll_data)

@app.route('/reset_responses')
@login_required
def reset_responses():
    user = User.query.get(session['user_id'])
    Response.query.filter_by(user_id=user.id).delete()
    db.session.commit()
    flash('Your responses have been reset. You can now answer the polls again.', 'success')
    return redirect(url_for('polls'))

@app.route('/forum')
@login_required
def forum():
    forums = ForumPost.query.order_by(ForumPost.date_posted.desc()).all()
    return render_template('forum.html', forums=forums)

@app.route('/forum/new', methods=['GET', 'POST'])
@login_required
def create_forum():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        description = request.form['description']
        user = User.query.get(session['user_id'])
        new_forum = ForumPost(title=title, content=content, description=description, author=user)
        db.session.add(new_forum)
        db.session.commit()
        flash('Your forum has been created!', 'success')
        return redirect(url_for('forum'))
    return render_template('create_forum.html')

@app.route('/forum/<int:forum_id>', methods=['GET', 'POST'])
@login_required
def forum_details(forum_id):
    forum = ForumPost.query.get_or_404(forum_id)
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            user = User.query.get(session['user_id'])
            new_comment = Comment(content=content, author=user, forum_post=forum)
            db.session.add(new_comment)
            if forum.comment_count is None:
                forum.comment_count = 1
            else:
                forum.comment_count += 1
            db.session.commit()
            flash('Your comment has been added!', 'success')
        return redirect(url_for('forum_details', forum_id=forum_id))
    comments = Comment.query.filter_by(forum_post_id=forum_id).order_by(Comment.date_posted.desc()).all()
    return render_template('forum_details.html', forum=forum, comments=comments)

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.author.id != session['user_id']:
        flash('You are not authorized to delete this comment.', 'danger')
        return redirect(url_for('forum_details', forum_id=comment.forum_post_id))
    
    forum = comment.forum_post
    if forum.comment_count is not None:
        forum.comment_count = max(0, forum.comment_count - 1)
    db.session.delete(comment)
    db.session.commit()
    flash('Your comment has been deleted.', 'success')
    return redirect(url_for('forum_details', forum_id=forum.id))