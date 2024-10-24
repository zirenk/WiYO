from app import app, db
import logging
from models import User, Poll, Response, ForumPost, Comment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_test_database():
    with app.app_context():
        try:
            logger.info("Starting database setup...")
            
            # Drop all tables first
            logger.info("Dropping existing tables...")
            db.drop_all()
            
            # Create all tables
            logger.info("Creating tables...")
            db.create_all()
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"Created tables: {tables}")
            
            # Verify required tables exist
            required_tables = ['user', 'poll', 'response', 'forum_post', 'comment']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                logger.error(f"Missing tables: {missing_tables}")
                return False
                
            logger.info("All required tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up test database: {str(e)}")
            return False

if __name__ == "__main__":
    setup_test_database()
