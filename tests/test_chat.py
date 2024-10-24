import pytest
import json
from app import db
import os
from unittest.mock import patch, MagicMock

def test_chat_page_access(auth_client):
    response = auth_client.get('/chat')
    assert response.status_code == 200
    assert b'Chat with WiYO AI' in response.data

@patch('openai.OpenAI')
def test_message_sending(mock_openai_class, auth_client):
    # Set up mock response
    mock_message = MagicMock()
    mock_message.content = 'Test response'
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    
    # Configure mock OpenAI client
    mock_client = mock_openai_class.return_value
    mock_client.chat.completions.create.return_value = mock_completion

    response = auth_client.post('/chat',
                             data=json.dumps({'user_message': 'Hello'}),
                             content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'ai_message' in data
    assert data['ai_message'] == 'Test response'

@patch('openai.OpenAI')
def test_demographics_inclusion(mock_openai_class, auth_client, test_user):
    demographics_data = {
        'age': '25',
        'occupation': 'developer'
    }
    
    with auth_client.application.app_context():
        test_user.demographics = demographics_data
        db.session.commit()
        
        # Set up mock response
        mock_message = MagicMock()
        mock_message.content = 'Response with demographics'
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        
        # Configure mock OpenAI client
        mock_client = mock_openai_class.return_value
        mock_client.chat.completions.create.return_value = mock_completion
        
        response = auth_client.post('/chat',
                                data=json.dumps({'user_message': 'Tell me about myself'}),
                                content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'ai_message' in data
        assert data['ai_message'] == 'Response with demographics'

def test_error_handling(auth_client):
    response = auth_client.post('/chat',
                             data=json.dumps({'invalid_key': 'value'}),
                             content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
