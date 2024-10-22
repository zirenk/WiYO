from flask import jsonify, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, login_user, logout_user, current_user
from app import app, db
from models import User
from werkzeug.security import check_password_hash
from utils import generate_login_code, generate_username

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        login_code = request.form.get('login_code')
        user = User.query.filter_by(login_code=login_code).first()
        
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid login code. Please try again.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

@app.route('/demographics', methods=['GET', 'POST'])
@login_required
def demographics():
    edit_mode = request.args.get('edit', 'false') == 'true'
    
    if request.method == 'POST':
        if request.is_json:
            # Handle AJAX request
            data = request.json
            current_user.demographics = data
            db.session.commit()
            return jsonify(success=True, message="Demographics updated successfully")
        else:
            # Handle traditional form submission
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

# Add other routes here...
