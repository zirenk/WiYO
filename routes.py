from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, Poll, Response, ForumPost, Comment
from app import app
from functools import wraps
import traceback
from utils import generate_login_code, generate_username
from sqlalchemy import func

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
    if user:
        return render_template('dashboard.html', username=user.username)
    else:
        flash('User not found. Please log in again.', 'danger')
        return redirect(url_for('login'))

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
    
    age_filter = request.args.get('age', 'All')
    gender_filter = request.args.get('gender', 'All')
    education_filter = request.args.get('education', 'All')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            filtered_results = get_filtered_poll_results(poll_id, age_filter, gender_filter, education_filter)
            return jsonify({
                'poll_data': {
                    'question': poll.question,
                    'results': filtered_results
                }
            })
        except Exception as e:
            app.logger.error(f"Error in results route: {str(e)}")
            app.logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500

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

def get_filtered_poll_results(poll_id, age_filter, gender_filter, education_filter):
    poll = Poll.query.get(poll_id)
    if not poll:
        return {}

    results = {choice: 0 for choice in poll.choices}

    query = db.session.query(Response, User).join(User).filter(Response.poll_id == poll_id)

    if age_filter != 'All':
        age_range = age_filter.split('-')
        if len(age_range) == 2:
            query = query.filter(func.cast(User.demographics['age'].astext, db.Integer).between(int(age_range[0]), int(age_range[1])))
        elif age_filter == '55+':
            query = query.filter(func.cast(User.demographics['age'].astext, db.Integer) >= 55)

    if gender_filter != 'All':
        query = query.filter(User.demographics['gender'].astext == gender_filter)

    if education_filter != 'All':
        query = query.filter(User.demographics['education'].astext == education_filter)

    responses = query.all()

    for response, user in responses:
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
        title = request.form['title']
        description = request.form['description']
        content = request.form['content']
        user_id = session['user_id']

        new_forum = ForumPost(title=title, description=description, content=content, user_id=user_id)
        db.session.add(new_forum)
        db.session.commit()

        flash('Your forum post has been created!', 'success')
        return redirect(url_for('forum'))

    return render_template('create_forum.html')

@app.route('/forum/<int:forum_id>', methods=['GET', 'POST'])
@login_required
def forum_details(forum_id):
    forum = ForumPost.query.get_or_404(forum_id)
    
    if request.method == 'POST':
        content = request.form['content']
        user_id = session['user_id']
        
        new_comment = Comment(content=content, user_id=user_id, forum_post_id=forum_id)
        db.session.add(new_comment)
        forum.comment_count += 1
        db.session.commit()
        
        flash('Your comment has been added!', 'success')
        return redirect(url_for('forum_details', forum_id=forum_id))
    
    comments = Comment.query.filter_by(forum_post_id=forum_id).order_by(Comment.date_posted.desc()).all()
    return render_template('forum_details.html', forum=forum, comments=comments)

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != session['user_id']:
        flash('You do not have permission to delete this comment.', 'danger')
        return redirect(url_for('forum_details', forum_id=comment.forum_post_id))
    
    forum = comment.forum_post
    forum.comment_count -= 1
    db.session.delete(comment)
    db.session.commit()
    
    flash('Your comment has been deleted.', 'success')
    return redirect(url_for('forum_details', forum_id=comment.forum_post_id))

@app.route('/demographics', methods=['GET', 'POST'])
@login_required
def demographics():
    user = User.query.get(session['user_id'])
    edit_mode = request.args.get('edit', 'false') == 'true'
    
    if request.method == 'POST':
        if 'edit_demographics' in request.form:
            return redirect(url_for('demographics', edit='true'))
        
        user.demographics = {
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
    
    return render_template('demographics.html', user=user, edit_mode=edit_mode)