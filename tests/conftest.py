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
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
        
        # Create all tables
        db.create_all()
        
        yield app
        
        # Clean up
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app_context):
    with app.test_client() as client:
        yield client
        # Clean up after each test
        db.session.rollback()

@pytest.fixture(scope='function')
def test_user(app_context):
    # Create a test user
    user = User()
    user.username = "TestUser123"
    user.login_code = "12345678"
    db.session.add(user)
    db.session.commit()
    
    yield user
    
    # Clean up
    db.session.delete(user)
    db.session.commit()

@pytest.fixture(scope='function')
def auth_client(client, test_user):
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
    return client

@pytest.fixture(scope='function')
def test_poll(app_context):
    # Create a test poll
    poll = Poll()
    poll.number = 1
    poll.question = "Test Poll?"
    poll.choices = ["Option 1", "Option 2"]
    db.session.add(poll)
    db.session.commit()
    
    yield poll
    
    # Clean up
    db.session.delete(poll)
    db.session.commit()
