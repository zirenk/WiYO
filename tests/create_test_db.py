import os
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app import app, db
import logging
from models import User, Poll, Response, ForumPost, Comment
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_test_database():
    with app.app_context():
        try:
            logger.info("Starting database setup...")
            
            # Drop all existing tables and sequences
            logger.info("Dropping existing tables and sequences...")
            db.session.execute(text('DROP SCHEMA IF EXISTS public CASCADE'))
            db.session.execute(text('CREATE SCHEMA public'))
            db.session.commit()
            
            # Create all tables
            logger.info("Creating tables...")
            db.create_all()
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"Created tables: {tables}")
            
            # Create indexes
            logger.info("Creating indexes...")
            db.session.execute(text('''
                CREATE INDEX IF NOT EXISTS idx_user_login_code ON "user" (login_code);
                CREATE INDEX IF NOT EXISTS idx_user_username ON "user" (username);
                CREATE INDEX IF NOT EXISTS idx_poll_number ON poll (number);
                CREATE INDEX IF NOT EXISTS idx_response_user_poll ON response (user_id, poll_id);
            '''))
            db.session.commit()
            
            logger.info("Database setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up test database: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    setup_test_database()
