from flask import jsonify, render_template, request, redirect, url_for, flash, session
from app import app, db
from models import User
from flask_login import login_required, current_user

@app.route('/demographics', methods=['GET', 'POST'])
@login_required
def demographics():
    user = User.query.get(current_user.id)
    edit_mode = request.args.get('edit', 'false') == 'true'
    
    if request.method == 'POST':
        try:
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
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify(success=True, message='Demographics updated successfully!')
            else:
                flash('Demographics updated successfully!', 'success')
                return redirect(url_for('demographics'))
        except Exception as e:
            db.session.rollback()
            error_message = f'Error updating demographics: {str(e)}'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify(success=False, error=error_message), 400
            else:
                flash(error_message, 'danger')
                return redirect(url_for('demographics'))
    
    return render_template('demographics.html', user=user, edit_mode=edit_mode)
