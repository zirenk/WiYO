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
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
        
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        login_code = request.form.get('login_code')
        remember_me = request.form.get('remember_me') == 'true'
        
        if not login_code or not login_code.isdigit() or len(login_code) != 8:
            return jsonify({'success': False, 'error': 'Please enter a valid 8-digit login code.'})
            
        user = User.query.filter_by(login_code=login_code).first()
        if not user:
            return jsonify({'success': False, 'error': 'Invalid login code'})
            
        login_user(user, remember=remember_me)
        return jsonify({'success': True, 'redirect': url_for('dashboard')})
        
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/create_wiyo_account', methods=['GET', 'POST'])
def create_wiyo_account():
    if request.method == 'POST':
        login_code = generate_login_code()
        username = generate_username()
        
        user = User()
        user.username = username
        user.login_code = login_code
        
        db.session.add(user)
        db.session.commit()
        
        return render_template('account_created.html', login_code=login_code, username=username)
        
    return render_template('create_wiyo_account.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

@app.route('/polls')
@login_required
def polls():
    # Get next unanswered poll for the user
    answered_polls = Response.query.filter_by(user_id=current_user.id).with_entities(Response.poll_id).all()
    answered_poll_ids = [p[0] for p in answered_polls]
    
    next_poll = Poll.query.filter(~Poll.id.in_(answered_poll_ids)).order_by(Poll.number).first()
    
    if not next_poll:
        return render_template('polls.html', no_polls=True)
        
    return render_template('polls.html', poll=next_poll)

@app.route('/submit_poll', methods=['POST'])
@login_required
def submit_poll():
    poll_id = request.form.get('poll_id')
    choice = request.form.get('choice')
    
    if not poll_id or not choice:
        flash('Invalid submission', 'error')
        return redirect(url_for('polls'))
        
    poll = Poll.query.get_or_404(poll_id)
    
    # Check if user has already responded
    existing_response = Response.query.filter_by(
        user_id=current_user.id,
        poll_id=poll_id
    ).first()
    
    if existing_response:
        flash('You have already responded to this poll', 'error')
        return redirect(url_for('polls'))
        
    # Create new response
    response = Response(
        user_id=current_user.id,
        poll_id=poll_id,
        choice=choice
    )
    db.session.add(response)
    db.session.commit()
    
    return redirect(url_for('results', poll_id=poll_id, just_submitted=True))

@app.route('/results/<int:poll_id>')
@login_required
def results(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Handle AJAX request for filtered results
        age = request.args.get('age', 'All')
        gender = request.args.get('gender', 'All')
        education = request.args.get('education', 'All')
        
        # Get all responses for this poll
        responses = Response.query.filter_by(poll_id=poll_id).all()
        results = {choice: 0 for choice in poll.choices}
        
        for response in responses:
            user = response.user
            if not user.demographics:
                continue
                
            # Apply demographic filters
            if ((age == 'All' or user.demographics.get('age') == age) and
                (gender == 'All' or user.demographics.get('gender') == gender) and
                (education == 'All' or user.demographics.get('education') == education)):
                results[response.choice] += 1
                
        return jsonify({
            'success': True,
            'poll_data': {
                'question': poll.question,
                'results': results
            }
        })
    
    # Calculate initial results
    responses = Response.query.filter_by(poll_id=poll_id).all()
    results = {choice: 0 for choice in poll.choices}
    for response in responses:
        results[response.choice] += 1
        
    poll_data = {
        'question': poll.question,
        'results': results
    }
    
    just_submitted = request.args.get('just_submitted', False)
    return render_template('results.html', poll=poll, poll_data=poll_data, just_submitted=just_submitted)

@app.route('/demographics', methods=['GET', 'POST'])
@login_required
def demographics():
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = request.get_json()
            current_user.demographics = data
            db.session.commit()
            return jsonify({'success': True})
            
    edit_mode = request.args.get('edit', 'false') == 'true'
    return render_template('demographics.html', user=current_user, edit_mode=edit_mode)

@app.route('/forum')
@login_required
def forum():
    forums = ForumPost.query.order_by(ForumPost.date_posted.desc()).all()
    return render_template('forum.html', forums=forums)

@app.route('/forum/create', methods=['GET', 'POST'])
@login_required
def create_forum():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        content = request.form.get('content')
        
        if not all([title, description, content]):
            flash('All fields are required', 'error')
            return redirect(url_for('create_forum'))
            
        forum_post = ForumPost(
            title=title,
            description=description,
            content=content,
            user_id=current_user.id
        )
        db.session.add(forum_post)
        db.session.commit()
        
        return redirect(url_for('forum'))
        
    return render_template('create_forum.html')

@app.route('/forum/<int:forum_id>', methods=['GET', 'POST'])
@login_required
def forum_details(forum_id):
    forum = ForumPost.query.get_or_404(forum_id)
    
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            comment = Comment(
                content=content,
                user_id=current_user.id,
                forum_post_id=forum_id
            )
            db.session.add(comment)
            forum.comment_count += 1
            db.session.commit()
            
    comments = Comment.query.filter_by(forum_post_id=forum_id).order_by(Comment.date_posted.desc()).all()
    return render_template('forum_details.html', forum=forum, comments=comments)

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.user_id != current_user.id:
        flash('You can only delete your own comments', 'error')
        return redirect(url_for('forum_details', forum_id=comment.forum_post_id))
        
    forum_post = comment.forum_post
    forum_post.comment_count -= 1
    
    db.session.delete(comment)
    db.session.commit()
    
    return redirect(url_for('forum_details', forum_id=comment.forum_post_id))

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
@login_required
def chat_message():
    if not request.is_json:
        return jsonify({'error': 'Invalid request format'}), 400
        
    data = request.get_json()
    user_message = data.get('user_message')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
        
    try:
        # Create chat message with user demographics context
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant that provides personalized responses based on user demographics."},
            {"role": "user", "content": f"User demographics: {current_user.demographics}\nMessage: {user_message}"}
        ]
        
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150
        )
        
        ai_message = response.choices[0].message.content
        return jsonify({'ai_message': ai_message})
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return jsonify({'error': 'Failed to process message'}), 500

@app.route('/chat/status')
@login_required
def chat_status():
    # This endpoint would be used for long-running chat operations
    # For now, we'll just return a completed status
    return jsonify({
        'status': 'complete',
        'ai_message': 'Message processed successfully'
    })
