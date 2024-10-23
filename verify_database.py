from app import app, db
from models import User, Poll, Response, ForumPost, Comment
from sqlalchemy import inspect
from datetime import datetime

def verify_database():
    with app.app_context():
        inspector = inspect(db.engine)
        required_tables = ['user', 'poll', 'response', 'forum_post', 'comment']
        
        print("1. Checking table existence:")
        print("-" * 50)
        existing_tables = inspector.get_table_names()
        for table in required_tables:
            status = "✓" if table in existing_tables else "✗"
            print(f"{status} {table}")
        
        print("\n2. Verifying table schemas:")
        print("-" * 50)
        for table in existing_tables:
            print(f"\nTable: {table}")
            columns = inspector.get_columns(table)
            for column in columns:
                print(f"  - {column['name']} ({column['type']})")
        
        print("\n3. Testing read/write operations:")
        print("-" * 50)
        try:
            # Create test user
            test_user = User(username="TestUser123", login_code="99999999")
            db.session.add(test_user)
            db.session.commit()
            print("✓ User creation successful")
            
            # Create test poll
            test_poll = Poll(number=999, question="Test Question", choices=["A", "B", "C"])
            db.session.add(test_poll)
            db.session.commit()
            print("✓ Poll creation successful")
            
            # Create test response
            test_response = Response(user_id=test_user.id, poll_id=test_poll.id, choice="A")
            db.session.add(test_response)
            db.session.commit()
            print("✓ Response creation successful")
            
            # Create test forum post
            test_post = ForumPost(
                title="Test Post",
                content="Test Content",
                description="Test Description",
                user_id=test_user.id
            )
            db.session.add(test_post)
            db.session.commit()
            print("✓ Forum post creation successful")
            
            # Create test comment
            test_comment = Comment(
                content="Test Comment",
                user_id=test_user.id,
                forum_post_id=test_post.id
            )
            db.session.add(test_comment)
            db.session.commit()
            print("✓ Comment creation successful")
            
            print("\n4. Verifying relationships:")
            print("-" * 50)
            # Verify user -> responses relationship
            user = User.query.filter_by(username="TestUser123").first()
            print(f"✓ User -> Responses: {user.responses.count() > 0}")
            
            # Verify user -> forum posts relationship
            print(f"✓ User -> Forum Posts: {user.forum_posts.count() > 0}")
            
            # Verify user -> comments relationship
            print(f"✓ User -> Comments: {user.comments.count() > 0}")
            
            # Verify poll -> responses relationship
            poll = Poll.query.filter_by(number=999).first()
            print(f"✓ Poll -> Responses: {poll.responses.count() > 0}")
            
            # Verify forum post -> comments relationship
            forum_post = ForumPost.query.filter_by(title="Test Post").first()
            print(f"✓ Forum Post -> Comments: {forum_post.comments.count() > 0}")
            
            # Clean up test data
            db.session.delete(test_comment)
            db.session.delete(test_post)
            db.session.delete(test_response)
            db.session.delete(test_poll)
            db.session.delete(test_user)
            db.session.commit()
            print("\nTest data cleaned up successfully")
            
        except Exception as e:
            print(f"Error during testing: {str(e)}")
            db.session.rollback()
            return False
            
        return True

if __name__ == "__main__":
    verify_database()
