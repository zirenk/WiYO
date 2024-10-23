import pytest
from flask import session
from app import db
from models import User
from utils import generate_login_code, generate_username

def test_login_page_access(test_client):
    """Test accessing the login page"""
    response = test_client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Enter your 8-digit login code' in response.data

def test_login_valid_credentials(test_client, test_user):
    """Test login with valid credentials"""
    # First ensure user exists
    with test_client.application.app_context():
        user = User.query.filter_by(login_code=test_user['login_code']).first()
        assert user is not None

    # Attempt login with AJAX request
    response = test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'true'
    }, headers={'X-Requested-With': 'XMLHttpRequest'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'redirect' in data
    
    # Verify session
    with test_client.session_transaction() as sess:
        assert 'user_id' in sess

def test_login_invalid_credentials(test_client):
    """Test login with invalid credentials"""
    response = test_client.post('/login', data={
        'login_code': '00000000',
        'remember_me': 'false'
    }, headers={'X-Requested-With': 'XMLHttpRequest'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is False
    assert 'Invalid login code' in data['error']
    
    # Verify session
    with test_client.session_transaction() as sess:
        assert 'user_id' not in sess

def test_logout(test_client, test_user):
    """Test logout functionality"""
    # First login
    test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'false'
    }, headers={'X-Requested-With': 'XMLHttpRequest'})
    
    # Then logout
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out' in response.data
    
    # Verify session
    with test_client.session_transaction() as sess:
        assert 'user_id' not in sess

def test_create_account(test_client):
    """Test user creation"""
    response = test_client.post('/create_wiyo_account', follow_redirects=True)
    assert response.status_code == 200
    assert b'Your WiYO account has been created successfully!' in response.data
    
    # Verify that a new user was created in the database
    with test_client.application.app_context():
        user = User.query.order_by(User.id.desc()).first()
        assert user is not None
        assert len(user.login_code) == 8
        assert user.username.startswith('Human')

def test_remember_me(test_client, test_user):
    """Test remember me functionality"""
    response = test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'true'
    }, headers={'X-Requested-With': 'XMLHttpRequest'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'redirect' in data
