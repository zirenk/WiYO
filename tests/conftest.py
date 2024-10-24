import pytest
from app import app, db
from models import User, Poll, Response, ForumPost, Comment
import os

@pytest.fixture(scope='session')
def app_context():
    with app.app_context():
        # Configure test database
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        # Create all tables in test database
        db.create_all()
        
        yield app
        
        # Clean up
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app_context):
    with app.test_client() as client:
        # Clear any existing data
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
        
        yield client
        
        # Clean up after each test
        db.session.rollback()

@pytest.fixture(scope='function')
def test_user(client):
    with app.app_context():
        user = User(username="TestUser123", login_code="12345678")
        db.session.add(user)
        db.session.commit()
        
        yield user

@pytest.fixture(scope='function')
def auth_client(client, test_user):
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
        session['_fresh'] = True
    return client

@pytest.fixture(scope='function')
def test_poll(client):
    with app.app_context():
        poll = Poll(number=1, question="Test Poll?", choices=["Option 1", "Option 2"])
        db.session.add(poll)
        db.session.commit()
        
        yield poll
