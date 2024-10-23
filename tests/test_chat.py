import pytest
from flask import session
import json

def test_chat_page_access(test_client, test_user):
    """Test accessing chat page"""
    # Login first
    test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'false'
    })
    
    response = test_client.get('/chat')
    assert response.status_code == 200
    assert b'Chat with WiYO AI' in response.data

def test_message_sending(test_client, test_user):
    """Test sending a message"""
    # Login
    test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'false'
    })
    
    # Send a message
    message_data = {
        'user_message': 'Hello, AI!'
    }
    
    response = test_client.post('/chat',
                              json=message_data,
                              headers={'X-Requested-With': 'XMLHttpRequest'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'ai_message' in data or 'status' in data

def test_ai_response(test_client, test_user):
    """Test receiving AI response"""
    # Login
    test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'false'
    })
    
    # Send a message and check response
    message_data = {
        'user_message': 'What is your name?'
    }
    
    response = test_client.post('/chat',
                              json=message_data,
                              headers={'X-Requested-With': 'XMLHttpRequest'})
    
    assert response.status_code == 200
    data = response.get_json()
    if 'ai_message' in data:
        assert len(data['ai_message']) > 0
    elif 'status' in data:
        assert data['status'] in ['queued', 'complete']

def test_demographics_inclusion(test_client, test_user):
    """Test demographics inclusion in AI context"""
    # Login
    test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'false'
    })
    
    # Set demographics first
    demographics_data = {
        'age': '25',
        'gender': 'female',
        'education': 'bachelors'
    }
    test_client.post('/demographics',
                    json=demographics_data,
                    headers={'X-Requested-With': 'XMLHttpRequest'})
    
    # Send a message
    message_data = {
        'user_message': 'Tell me about yourself'
    }
    
    response = test_client.post('/chat',
                              json=message_data,
                              headers={'X-Requested-With': 'XMLHttpRequest'})
    
    assert response.status_code == 200

def test_rate_limiting(test_client, test_user):
    """Test rate limiting functionality"""
    # Login
    test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'false'
    })
    
    # Send multiple requests quickly
    message_data = {
        'user_message': 'Test message'
    }
    
    responses = []
    for _ in range(5):  # Send 5 requests quickly
        response = test_client.post('/chat',
                                  json=message_data,
                                  headers={'X-Requested-With': 'XMLHttpRequest'})
        responses.append(response)
    
    # At least one response should indicate rate limiting
    assert any(r.status_code == 429 for r in responses) or \
           any('rate limit' in r.get_json().get('error', '').lower() for r in responses if r.status_code == 200)

def test_error_handling(test_client, test_user):
    """Test error handling in chat"""
    # Login
    test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'false'
    })
    
    # Test with invalid request format
    response = test_client.post('/chat', data='invalid json')
    assert response.status_code == 400
    
    # Test with empty message
    response = test_client.post('/chat',
                              json={'user_message': ''},
                              headers={'X-Requested-With': 'XMLHttpRequest'})
    assert response.status_code == 400
    
    # Test with missing message field
    response = test_client.post('/chat',
                              json={},
                              headers={'X-Requested-With': 'XMLHttpRequest'})
    assert response.status_code == 400
