from app import app, db
from models import User, Poll, Response, ForumPost, Comment
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_tables():
    with app.app_context():
        logger.info("Starting table creation...")
        try:
            # Drop all tables first to ensure clean slate
            logger.info("Dropping existing tables...")
            db.drop_all()
            
            # Create all tables
            logger.info("Creating tables...")
            db.create_all()
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"Created tables: {tables}")
            
            # Commit the transaction
            db.session.commit()
            print("Tables created successfully!")
            return True
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    create_tables()
