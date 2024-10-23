from app import app, db
from models import User, Poll, Response, ForumPost, Comment

def create_tables():
    with app.app_context():
        db.create_all()
        print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()
