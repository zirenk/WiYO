import pytest
from flask import session
from app import db
from models import ForumPost, Comment

def test_forum_page_access(test_client, test_user):
    """Test accessing forum page"""
    # Login first
    test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'false'
    })
    
    response = test_client.get('/forum')
    assert response.status_code == 200
    assert b'Forums' in response.data

def test_forum_post_creation(test_client, test_user):
    """Test creating a forum post"""
    # Login
    test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'false'
    })
    
    # Create a forum post
    post_data = {
        'title': 'Test Forum Post',
        'description': 'Test Description',
        'content': 'Test Content'
    }
    
    response = test_client.post('/create_forum',
                              data=post_data,
                              follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Test Forum Post' in response.data
    
    # Verify post was created in database
    with test_client.application.app_context():
        post = ForumPost.query.filter_by(title='Test Forum Post').first()
        assert post is not None
        assert post.content == 'Test Content'

def test_forum_post_viewing(test_client, test_user):
    """Test viewing a forum post"""
    # Login
    test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'false'
    })
    
    # Create a post first
    with test_client.application.app_context():
        post = ForumPost(
            title='Test Post',
            content='Test Content',
            description='Test Description',
            user_id=test_user['user'].id
        )
        db.session.add(post)
        db.session.commit()
        post_id = post.id
    
    # View the post
    response = test_client.get(f'/forum/{post_id}')
    assert response.status_code == 200
    assert b'Test Post' in response.data
    assert b'Test Content' in response.data

def test_comment_creation_and_deletion(test_client, test_user):
    """Test creating and deleting comments"""
    # Login
    test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'false'
    })
    
    # Create a post first
    with test_client.application.app_context():
        post = ForumPost(
            title='Test Post',
            content='Test Content',
            description='Test Description',
            user_id=test_user['user'].id
        )
        db.session.add(post)
        db.session.commit()
        post_id = post.id
    
    # Add a comment
    comment_data = {
        'content': 'Test Comment'
    }
    
    response = test_client.post(f'/forum/{post_id}',
                              data=comment_data,
                              follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Test Comment' in response.data
    
    # Verify comment was added
    with test_client.application.app_context():
        comment = Comment.query.filter_by(content='Test Comment').first()
        assert comment is not None
        
        # Delete the comment
        comment_id = comment.id
    
    # Delete comment
    response = test_client.post(f'/delete_comment/{comment_id}',
                              follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Test Comment' not in response.data

def test_forum_listing(test_client, test_user):
    """Test forum posts listing"""
    # Login
    test_client.post('/login', data={
        'login_code': test_user['login_code'],
        'remember_me': 'false'
    })
    
    # Create multiple posts
    with test_client.application.app_context():
        posts = [
            ForumPost(title=f'Post {i}',
                     content=f'Content {i}',
                     description=f'Description {i}',
                     user_id=test_user['user'].id)
            for i in range(3)
        ]
        db.session.add_all(posts)
        db.session.commit()
    
    # Get forum listing
    response = test_client.get('/forum')
    assert response.status_code == 200
    
    # Check if all posts are listed
    for i in range(3):
        assert f'Post {i}'.encode() in response.data
