import pytest
from app import app, db
from models import User, Poll, Response, ForumPost, Comment
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope='session', autouse=True)
def setup_test_environment():
    # Set test configurations
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    
    # Push an application context
    ctx = app.app_context()
    ctx.push()
    
    # Create all tables
    logger.info("Creating test database tables...")
    db.create_all()
    
    yield
    
    # Clean up
    logger.info("Cleaning up test database...")
    db.session.remove()
    db.drop_all()
    ctx.pop()

@pytest.fixture(scope='function')
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def test_user():
    user = User(
        username="TestUser123",
        login_code="12345678"
    )
    db.session.add(user)
    db.session.commit()
    yield user
    db.session.delete(user)
    db.session.commit()

@pytest.fixture(scope='function')
def auth_client(client, test_user):
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id
        sess['_fresh'] = True
    return client

@pytest.fixture(scope='function')
def test_poll():
    poll = Poll(
        number=1,
        question="Test Poll?",
        choices=["Option 1", "Option 2"]
    )
    db.session.add(poll)
    db.session.commit()
    yield poll
    db.session.delete(poll)
    db.session.commit()
