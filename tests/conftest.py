import pytest
from app import app, db
from models import User, Poll, Response
from utils import generate_login_code, generate_username
import os

@pytest.fixture(scope='session')
def test_client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    
    # Initialize the test client
    with app.test_client() as client:
        with app.app_context():
            # Create all tables
            db.create_all()
            yield client
            # Clean up
            db.session.remove()
            db.drop_all()

@pytest.fixture
def test_user(test_client):
    """Create a test user"""
    with app.app_context():
        login_code = generate_login_code()
        username = generate_username()
        user = User()
        user.login_code = login_code
        user.username = username
        db.session.add(user)
        db.session.commit()
        
        yield {"user": user, "login_code": login_code, "username": username}
        
        # Cleanup
        db.session.delete(user)
        db.session.commit()

@pytest.fixture
def test_poll(test_client):
    """Create a test poll"""
    with app.app_context():
        poll = Poll()
        poll.number = 1
        poll.question = "Test Poll Question?"
        poll.choices = ["Option 1", "Option 2", "Option 3"]
        db.session.add(poll)
        db.session.commit()
        
        yield poll
        
        # Cleanup
        db.session.delete(poll)
        db.session.commit()

@pytest.fixture(autouse=True)
def setup_database():
    """Setup database before each test"""
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.session.close_all()
        db.drop_all()
