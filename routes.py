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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_code = request.form.get('login_code')
        remember_me = bool(request.form.get('remember_me'))
        
        user = User.query.filter_by(login_code=login_code).first()
        
        if user:
            login_user(user, remember=remember_me)
            session['user_id'] = user.id
            if request.is_xhr:
                return jsonify({'success': True, 'redirect': url_for('dashboard')})
            return redirect(url_for('dashboard'))
        else:
            if request.is_xhr:
                return jsonify({'success': False, 'error': 'Invalid login code'})
            flash('Invalid login code', 'danger')
            
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

@app.route('/demographics', methods=['GET', 'POST'])
@login_required
def demographics():
    edit_mode = request.args.get('edit', 'false').lower() == 'true'
    
    if request.method == 'POST':
        if request.is_json:
            data = request.json
            current_user.demographics = data
            db.session.commit()
            return jsonify(success=True, message="Demographics updated successfully")
        else:
            current_user.demographics = {
                'age': request.form.get('age'),
                'gender': request.form.get('gender'),
                'education': request.form.get('education'),
                'employment': request.form.get('employment'),
                'marital_status': request.form.get('marital_status'),
                'income': request.form.get('income'),
                'location': request.form.get('location'),
                'ethnicity': request.form.get('ethnicity'),
                'political_affiliation': request.form.get('political_affiliation'),
                'religion': request.form.get('religion')
            }
            db.session.commit()
            flash('Demographics updated successfully!', 'success')
            return redirect(url_for('demographics'))
    
    return render_template('demographics.html', user=current_user, edit_mode=edit_mode)

@app.route('/polls')
@login_required
def polls():
    # Get all polls that the user hasn't responded to yet
    responded_polls = Response.query.filter_by(user_id=current_user.id, responded=True).with_entities(Response.poll_id).all()
    responded_poll_ids = [p[0] for p in responded_polls]
    
    next_poll = Poll.query.filter(~Poll.id.in_(responded_poll_ids)).order_by(Poll.number).first()
    
    if next_poll is None:
        return render_template('polls.html', no_polls=True)
    
    return render_template('polls.html', poll=next_poll, no_polls=False)

@app.route('/submit_poll', methods=['POST'])
@login_required
def submit_poll():
    poll_id = request.form.get('poll_id')
    choice = request.form.get('choice')
    
    if not poll_id or not choice:
        flash('Invalid submission', 'danger')
        return redirect(url_for('polls'))
    
    poll = Poll.query.get_or_404(poll_id)
    
    # Check if user has already responded
    existing_response = Response.query.filter_by(
        user_id=current_user.id,
        poll_id=poll_id
    ).first()
    
    if existing_response:
        flash('You have already responded to this poll', 'warning')
    else:
        response = Response(
            user_id=current_user.id,
            poll_id=poll_id,
            choice=choice,
            responded=True
        )
        db.session.add(response)
        db.session.commit()
        flash('Response submitted successfully', 'success')
    
    return redirect(url_for('results', poll_id=poll_id, just_submitted=True))

@app.route('/results/<int:poll_id>')
@login_required
def results(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    just_submitted = request.args.get('just_submitted', 'false').lower() == 'true'
    
    # Get all responses for this poll
    responses = Response.query.filter_by(poll_id=poll_id).all()
    
    # Count responses for each choice
    results = {}
    for choice in poll.choices:
        results[choice] = sum(1 for r in responses if r.choice == choice)
    
    poll_data = {
        'question': poll.question,
        'results': results
    }
    
    return render_template('results.html', poll=poll, poll_data=poll_data, just_submitted=just_submitted)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('login'))

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

# Add chat routes
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

@app.route('/forum')
@login_required
def forum():
    forums = ForumPost.query.order_by(ForumPost.date_posted.desc()).all()
    return render_template('forum.html', forums=forums)

@app.route('/create_forum', methods=['GET', 'POST'])
@login_required
def create_forum():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        content = request.form.get('content')
        
        post = ForumPost(
            title=title,
            description=description,
            content=content,
            author=current_user
        )
        db.session.add(post)
        db.session.commit()
        
        return redirect(url_for('forum'))
    
    return render_template('create_forum.html')

@app.route('/forum/<int:forum_id>', methods=['GET', 'POST'])
@login_required
def forum_details(forum_id):
    forum = ForumPost.query.get_or_404(forum_id)
    comments = Comment.query.filter_by(forum_post_id=forum_id).order_by(Comment.date_posted).all()
    
    if request.method == 'POST':
        content = request.form.get('content')
        comment = Comment(content=content, author=current_user, forum_post=forum)
        forum.comment_count += 1
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('forum_details', forum_id=forum_id))
    
    return render_template('forum_details.html', forum=forum, comments=comments)

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.author != current_user:
        flash('You can only delete your own comments', 'danger')
        return redirect(url_for('forum_details', forum_id=comment.forum_post_id))
    
    forum = comment.forum_post
    forum.comment_count -= 1
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully', 'success')
    return redirect(url_for('forum_details', forum_id=comment.forum_post_id))

@app.before_request
def check_first_request():
    if 'first_request' not in session:
        session['first_request'] = True
        db.create_all()
