import pytest
from models import User
from app import db
import json

def test_login_valid_credentials(client, test_user):
    response = client.post('/login', 
                         data=json.dumps({
                             'login_code': '12345678',
                             'remember_me': 'true'
                         }),
                         content_type='application/json',
                         headers={'X-Requested-With': 'XMLHttpRequest'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'redirect' in data

def test_login_invalid_credentials(client):
    response = client.post('/login',
                         data=json.dumps({
                             'login_code': '00000000',
                             'remember_me': 'false'
                         }),
                         content_type='application/json',
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
    # Test GET request
    response = client.get('/create_wiyo_account')
    assert response.status_code == 200
    assert b'Create WiYO Account' in response.data

    # Test POST request
    response = client.post('/create_wiyo_account')
    assert response.status_code == 200
    assert b'Login Code' in response.data

def test_remember_me(client, test_user):
    response = client.post('/login',
                         data=json.dumps({
                             'login_code': '12345678',
                             'remember_me': 'true'
                         }),
                         content_type='application/json',
                         headers={'X-Requested-With': 'XMLHttpRequest'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True

def test_protected_route_access(client, auth_client):
    # Test unauthorized access
    response = client.get('/dashboard')
    assert response.status_code == 302  # Redirect to login
    
    # Test authorized access
    response = auth_client.get('/dashboard')
    assert response.status_code == 200
    assert b'Welcome' in response.data
