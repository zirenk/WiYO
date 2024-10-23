import pytest
from app import db
from models import Poll, Response
from flask import session

def test_poll_creation(test_client, init_database):
    """Test creating a new poll"""
    with test_client.application.app_context():
        # Create a test poll
        poll = Poll(
            number=1,
            question="Test Poll Question?",
            choices=["Option 1", "Option 2", "Option 3"]
        )
        db.session.add(poll)
        db.session.commit()
        
        # Verify poll was created
        saved_poll = Poll.query.first()
        assert saved_poll is not None
        assert saved_poll.question == "Test Poll Question?"
        assert len(saved_poll.choices) == 3

def test_poll_response_submission(test_client, test_user, init_database):
    """Test submitting a response to a poll"""
    with test_client.application.app_context():
        # Create a test poll
        poll = Poll(
            number=1,
            question="Test Poll Question?",
            choices=["Option 1", "Option 2", "Option 3"]
        )
        db.session.add(poll)
        db.session.commit()
        
        # Login the test user
        test_client.post('/login', data={
            'login_code': test_user['login_code'],
            'remember_me': 'false'
        })
        
        # Submit response
        response = test_client.post('/submit_poll', data={
            'poll_id': poll.id,
            'choice': "Option 1"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify response was recorded
        poll_response = Response.query.filter_by(
            user_id=test_user['user'].id,
            poll_id=poll.id
        ).first()
        
        assert poll_response is not None
        assert poll_response.choice == "Option 1"

def test_poll_results_calculation(test_client, test_user, init_database):
    """Test calculating and displaying poll results"""
    with test_client.application.app_context():
        # Create a test poll
        poll = Poll(
            number=1,
            question="Test Poll Question?",
            choices=["Option 1", "Option 2", "Option 3"]
        )
        db.session.add(poll)
        db.session.commit()
        
        # Create some responses
        responses = [
            Response(user_id=test_user['user'].id, poll_id=poll.id, choice="Option 1"),
            Response(user_id=test_user['user'].id, poll_id=poll.id, choice="Option 1"),
            Response(user_id=test_user['user'].id, poll_id=poll.id, choice="Option 2")
        ]
        for response in responses:
            db.session.add(response)
        db.session.commit()
        
        # Login the test user
        test_client.post('/login', data={
            'login_code': test_user['login_code'],
            'remember_me': 'false'
        })
        
        # Get results
        response = test_client.get(f'/results/{poll.id}')
        assert response.status_code == 200
        
        # Verify results data
        results_data = response.get_json()
        assert results_data is not None
        assert 'poll_data' in results_data
        assert results_data['poll_data']['results']['Option 1'] == 2
        assert results_data['poll_data']['results']['Option 2'] == 1
