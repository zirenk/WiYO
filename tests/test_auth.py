import pytest
from flask import session
from app import db
from models import User

def test_login_valid_credentials(test_client, test_user):
    """Test login with valid credentials"""
    response = test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'true'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Welcome' in response.data
    assert 'user_id' in session

def test_login_invalid_credentials(test_client):
    """Test login with invalid credentials"""
    response = test_client.post('/login', data={
        'login_code': '00000000',
        'remember_me': 'false'
    })
    
    assert response.status_code == 200
    assert b'Invalid login code' in response.data
    assert 'user_id' not in session

def test_logout(test_client, test_user):
    """Test logout functionality"""
    # First login
    test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'false'
    })
    
    # Then logout
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out' in response.data
    assert 'user_id' not in session

def test_create_account(test_client):
    """Test user creation"""
    response = test_client.post('/create_wiyo_account', follow_redirects=True)
    assert response.status_code == 200
    assert b'Your WiYO account has been created successfully!' in response.data
    
    # Verify that a new user was created in the database
    with test_client.application.app_context():
        user = User.query.first()
        assert user is not None
        assert len(user.login_code) == 8
        assert user.username.startswith('Human')
