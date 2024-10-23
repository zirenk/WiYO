import pytest
from app import app, db
from models import User, Poll, Response
from utils import generate_login_code, generate_username

@pytest.fixture
def test_client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def init_database():
    # Create tables
    with app.app_context():
        db.create_all()
        yield db
        # Clean up / reset resources
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_user(init_database):
    # Create a test user
    with app.app_context():
        login_code = "12345678"
        username = "TestHuman123"
        user = User(login_code=login_code, username=username)
        db.session.add(user)
        db.session.commit()
        
        return {"user": user, "login_code": login_code, "username": username}
