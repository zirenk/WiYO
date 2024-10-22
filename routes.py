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
