import pytest
import json
from app import db

def test_chat_page_access(auth_client):
    response = auth_client.get('/chat')
    assert response.status_code == 200
    assert b'Chat with WiYO AI' in response.data

def test_message_sending(auth_client):
    response = auth_client.post('/chat',
                              data=json.dumps({'user_message': 'Hello'}),
                              content_type='application/json')
    assert response.status_code == 200
    assert 'ai_message' in response.json or 'status' in response.json

def test_ai_response(auth_client):
    response = auth_client.post('/chat',
                              data=json.dumps({'user_message': 'What can you help me with?'}),
                              content_type='application/json')
    assert response.status_code == 200
    assert 'ai_message' in response.json or 'status' in response.json

def test_demographics_inclusion(auth_client, test_user):
    demographics_data = {
        'age': '25',
        'occupation': 'developer'
    }
    
    with auth_client.application.app_context():
        test_user.demographics = demographics_data
        db.session.commit()
        
        response = auth_client.post('/chat',
                                  data=json.dumps({'user_message': 'Tell me about myself'}),
                                  content_type='application/json')
        assert response.status_code == 200

def test_rate_limiting(auth_client):
    # Test rapid requests
    for _ in range(5):
        response = auth_client.post('/chat',
                                  data=json.dumps({'user_message': 'Test message'}),
                                  content_type='application/json')
    
    # The last request should be rate limited
    assert response.status_code == 429

def test_error_handling(auth_client):
    response = auth_client.post('/chat',
                              data=json.dumps({'invalid_key': 'value'}),
                              content_type='application/json')
    assert response.status_code == 400
    assert 'error' in response.json
