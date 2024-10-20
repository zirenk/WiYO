from app import app, db
from models import User

def debug_user(username):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"User found: {user.username}, Login code: {user.login_code}")
            print(f"Demographics: {user.demographics}")
        else:
            print(f"User {username} not found in the database.")

if __name__ == "__main__":
    debug_user('Human4680893')
