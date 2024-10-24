import pytest
from models import User
from app import db
import json
from flask_login import login_user
from flask import session

def test_login_valid_credentials(client, test_user):
    response = client.post('/login', 
                         data={
                             'login_code': test_user.login_code,
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
    response = auth_client.get('/logout')
    assert response.status_code == 302  # Should redirect to login
    assert '/login' in response.location

def test_create_wiyo_account(client):
    response = client.post('/create_wiyo_account')
    assert response.status_code == 200
    assert b'Login Code' in response.data
    
    with client.application.app_context():
        user = User.query.filter(User.username.like('Human%')).first()
        assert user is not None
        assert len(user.login_code) == 8

def test_protected_route_access(app_context, client, test_user):
    # Test unauthorized access
    response = client.get('/dashboard')
    assert response.status_code == 302
    assert '/login' in response.location
    
    # Test authorized access
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id
        sess['_fresh'] = True
    
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert bytes(f'Welcome, {test_user.username}', 'utf-8') in response.data

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
