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
        
        # Drop and recreate tables
        db.drop_all()
        db.create_all()
        
        yield app
        
        # Clean up after all tests
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app_context):
    with app.test_client() as client:
        db.create_all()  # Ensure tables exist
        yield client
        db.session.remove()  # Remove session
        db.drop_all()  # Clean up tables

@pytest.fixture(scope='function')
def test_user(client):
    user = User(username="TestUser123", login_code="12345678")
    db.session.add(user)
    db.session.commit()
    yield user
    db.session.rollback()

@pytest.fixture(scope='function')
def auth_client(client, test_user):
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
        session['_fresh'] = True
    return client

@pytest.fixture(scope='function')
def test_poll(client):
    poll = Poll(number=1, question="Test Poll?", choices=["Option 1", "Option 2"])
    db.session.add(poll)
    db.session.commit()
    yield poll
    db.session.rollback()
