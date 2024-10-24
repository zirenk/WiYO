import pytest
import json
from models import User
from app import db

def test_demographics_page_access(auth_client):
    response = auth_client.get('/demographics')
    assert response.status_code == 200
    assert b'Demographics' in response.data

def test_demographics_form_submission(auth_client):
    demographics_data = {
        'age': '25',
        'gender': 'male',
        'education': 'bachelors',
        'employment': 'full_time',
        'marital_status': 'single',
        'income': '50k_75k',
        'location': 'New York',
        'ethnicity': 'white',
        'political_affiliation': 'independent',
        'religion': 'none'
    }
    
    response = auth_client.post('/demographics', 
                              data=json.dumps(demographics_data),
                              content_type='application/json')
    assert response.status_code == 200
    assert response.json['success'] == True

def test_demographics_data_retrieval(auth_client, test_user):
    demographics_data = {
        'age': '25',
        'gender': 'male'
    }
    
    with auth_client.application.app_context():
        test_user.demographics = demographics_data
        db.session.commit()
        
        response = auth_client.get('/demographics')
        assert response.status_code == 200
        assert b'25' in response.data
        assert b'male' in response.data

def test_edit_mode_toggle(auth_client):
    response = auth_client.get('/demographics')
    assert response.status_code == 200
    assert b'Edit Demographics' in response.data

def test_demographics_validation(auth_client):
    invalid_data = {
        'age': 'invalid',
        'gender': 'invalid'
    }
    
    response = auth_client.post('/demographics', 
                              data=json.dumps(invalid_data),
                              content_type='application/json')
    assert response.status_code == 400
