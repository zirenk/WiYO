import pytest
from models import Poll, Response
from app import db

def test_poll_creation(client, auth_client):
    poll = Poll(number=1, question="Test Poll?", choices=["Option 1", "Option 2"])
    with client.application.app_context():
        db.session.add(poll)
        db.session.commit()
        
        response = auth_client.get('/polls')
        assert response.status_code == 200
        assert b'Test Poll?' in response.data

def test_poll_response_submission(auth_client):
    poll = Poll(number=1, question="Test Poll?", choices=["Option 1", "Option 2"])
    with auth_client.application.app_context():
        db.session.add(poll)
        db.session.commit()
        
        response = auth_client.post('/submit_poll', data={
            'poll_id': poll.id,
            'choice': 'Option 1'
        })
        assert response.status_code == 302  # Redirect after submission

def test_poll_results_viewing(auth_client):
    poll = Poll(number=1, question="Test Poll?", choices=["Option 1", "Option 2"])
    with auth_client.application.app_context():
        db.session.add(poll)
        db.session.commit()
        
        response = auth_client.get(f'/results/{poll.id}')
        assert response.status_code == 200
        assert b'Test Poll?' in response.data

def test_poll_results_calculation(auth_client, test_user):
    poll = Poll(number=1, question="Test Poll?", choices=["Option 1", "Option 2"])
    with auth_client.application.app_context():
        db.session.add(poll)
        db.session.commit()
        
        # Add a response
        poll_response = Response(user_id=test_user.id, poll_id=poll.id, choice="Option 1")
        db.session.add(poll_response)
        db.session.commit()
        
        response = auth_client.get(f'/results/{poll.id}')
        assert response.status_code == 200
        assert b'Option 1' in response.data
