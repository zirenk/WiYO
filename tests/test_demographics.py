import pytest
from flask import session
from app import db
from models import User

def test_demographics_page_access(test_client, test_user):
    """Test accessing demographics page"""
    # Login first
    test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'false'
    })
    
    response = test_client.get('/demographics')
    assert response.status_code == 200
    assert b'Demographics' in response.data

def test_demographics_form_submission(test_client, test_user):
    """Test submitting demographics form"""
    # Login
    test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'false'
    })
    
    # Submit demographics data
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
    
    response = test_client.post('/demographics',
                              json=demographics_data,
                              headers={'X-Requested-With': 'XMLHttpRequest'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

    # Verify data was saved
    with test_client.application.app_context():
        user = User.query.get(test_user['user'].id)
        assert user.demographics['age'] == '25'
        assert user.demographics['gender'] == 'male'

def test_demographics_data_retrieval(test_client, test_user):
    """Test retrieving demographics data"""
    # Login
    test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'false'
    })
    
    # First set some demographics data
    with test_client.application.app_context():
        test_user['user'].demographics = {
            'age': '30',
            'gender': 'female'
        }
        db.session.commit()
    
    # Get demographics page
    response = test_client.get('/demographics')
    assert response.status_code == 200
    assert b'30' in response.data
    assert b'female' in response.data

def test_edit_mode_toggle(test_client, test_user):
    """Test toggling edit mode"""
    # Login
    test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'false'
    })
    
    response = test_client.get('/demographics')
    assert response.status_code == 200
    assert b'Edit Demographics' in response.data
    assert b'readonly' in response.data

def test_demographics_validation(test_client, test_user):
    """Test form validation"""
    # Login
    test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'false'
    })
    
    # Test invalid age
    invalid_data = {
        'age': '-1',  # Invalid age
        'gender': 'male',
        'education': 'bachelors'
    }
    
    response = test_client.post('/demographics',
                              json=invalid_data,
                              headers={'X-Requested-With': 'XMLHttpRequest'})
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
