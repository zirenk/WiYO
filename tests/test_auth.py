import pytest
from models import User
from app import db
import json
from flask_login import login_user

def test_login_valid_credentials(client, test_user):
    response = client.post('/login', 
                         data={
                             'login_code': '12345678',
                             'remember_me': 'false'
                         },
                         headers={'X-Requested-With': 'XMLHttpRequest'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'redirect' in data

def test_login_invalid_credentials(client):
    response = client.post('/login',
                         data={
                             'login_code': '00000000',
                             'remember_me': 'false'
                         },
                         headers={'X-Requested-With': 'XMLHttpRequest'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == False
    assert 'error' in data

def test_logout(auth_client):
    response = auth_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

def test_create_wiyo_account(client):
    response = client.post('/create_wiyo_account', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login Code' in response.data
    
    # Verify user was created in database
    with client.application.app_context():
        user = User.query.filter(User.username.like('Human%')).first()
        assert user is not None
        assert len(user.login_code) == 8

def test_protected_route_access(client, auth_client):
    # Test unauthorized access
    response = client.get('/dashboard')
    assert response.status_code == 302  # Should redirect to login
    
    # Test authorized access
    response = auth_client.get('/dashboard')
    assert response.status_code == 200
    assert b'Dashboard' in response.data

def test_remember_me_functionality(client, test_user):
    response = client.post('/login',
                         data={
                             'login_code': '12345678',
                             'remember_me': 'true'
                         },
                         headers={'X-Requested-With': 'XMLHttpRequest'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True

def test_login_code_validation(client):
    # Test too short code
    response = client.post('/login',
                         data={
                             'login_code': '123',
                             'remember_me': 'false'
                         },
                         headers={'X-Requested-With': 'XMLHttpRequest'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == False
    
    # Test non-numeric code
    response = client.post('/login',
                         data={
                             'login_code': 'abcdefgh',
                             'remember_me': 'false'
                         },
                         headers={'X-Requested-With': 'XMLHttpRequest'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == False
