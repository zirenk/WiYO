from app import app, db
from models import User

def debug_database():
    with app.app_context():
        # Check all users
        users = User.query.all()
        print(f"Total users in database: {len(users)}")
        
        if users:
            print("\nExisting users:")
            for user in users:
                print(f"Username: {user.username}")
                print(f"Login code: {user.login_code}")
                print(f"User ID: {user.id}")
                print("-" * 30)
        else:
            print("\nNo users found in database.")
            print("Creating a test user...")
            
            # Create a test user if no users exist
            test_user = User(
                username="Human12345678",
                login_code="12345678"
            )
            db.session.add(test_user)
            db.session.commit()
            print(f"Test user created with login code: 12345678")

if __name__ == "__main__":
    debug_database()
