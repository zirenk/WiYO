import pytest
from models import ForumPost, Comment
from app import db

def test_forum_page_access(auth_client):
    response = auth_client.get('/forum')
    assert response.status_code == 200
    assert b'Forums' in response.data

def test_forum_post_creation(auth_client, test_user):
    post_data = {
        'title': 'Test Post',
        'description': 'Test Description',
        'content': 'Test Content'
    }
    
    response = auth_client.post('/forum/create', data=post_data)
    assert response.status_code == 200
    
    with auth_client.application.app_context():
        post = ForumPost.query.filter_by(title='Test Post').first()
        assert post is not None
        assert post.user_id == test_user.id

def test_forum_post_viewing(auth_client, test_user):
    post = ForumPost(
        title='Test Post',
        description='Test Description',
        content='Test Content',
        user_id=test_user.id
    )
    
    with auth_client.application.app_context():
        db.session.add(post)
        db.session.commit()
        
        response = auth_client.get(f'/forum/{post.id}')
        assert response.status_code == 200
        assert b'Test Post' in response.data

def test_comment_creation_and_deletion(auth_client, test_user):
    post = ForumPost(
        title='Test Post',
        content='Test Content',
        user_id=test_user.id
    )
    
    with auth_client.application.app_context():
        db.session.add(post)
        db.session.commit()
        
        # Test comment creation
        response = auth_client.post(f'/forum/{post.id}', data={
            'content': 'Test Comment'
        })
        assert response.status_code == 200
        
        comment = Comment.query.filter_by(content='Test Comment').first()
        assert comment is not None
        
        # Test comment deletion
        response = auth_client.post(f'/delete_comment/{comment.id}')
        assert response.status_code == 302
        
        comment = Comment.query.filter_by(content='Test Comment').first()
        assert comment is None

def test_forum_listing(auth_client, test_user):
    posts = [
        ForumPost(title=f'Test Post {i}', content=f'Content {i}', user_id=test_user.id)
        for i in range(3)
    ]
    
    with auth_client.application.app_context():
        for post in posts:
            db.session.add(post)
        db.session.commit()
        
        response = auth_client.get('/forum')
        assert response.status_code == 200
        for i in range(3):
            assert f'Test Post {i}'.encode() in response.data
