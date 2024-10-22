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

        return redirect(url_for('results', poll_id=poll_id))
    except Exception as e:
        app.logger.error(f"Error in submit_poll: {str(e)}")
        app.logger.error(traceback.format_exc())
        flash('An error occurred while submitting your response. Please try again.', 'error')
        return redirect(url_for('polls'))

@app.route('/results/<int:poll_id>')
@login_required
def results(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    results = get_poll_results(poll_id)

    return render_template('results.html',
                           poll=poll,
                           poll_data={
                               'question': poll.question,
                               'results': results
                           })

def get_poll_results(poll_id):
    poll = Poll.query.get(poll_id)
    if not poll:
        return {}

    results = {choice: 0 for choice in poll.choices}
    responses = Response.query.filter_by(poll_id=poll_id).all()
    for response in responses:
        results[response.choice] += 1
    return results
