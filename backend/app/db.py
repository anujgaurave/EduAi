from pymongo import MongoClient
from app.config import Config
import logging

logger = logging.getLogger(__name__)

class Database:
    """Database connection manager"""
    
    def __init__(self):
        self.client = None
        self.db = None
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(Config.MONGODB_URI)
            self.db = self.client[Config.MONGODB_DB_NAME]
            
            # Verify connection
            self.db.command('ping')
            logger.info("MongoDB connected successfully")
            
            # Create necessary indexes
            self._create_indexes()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def _create_indexes(self):
        """Create necessary database indexes"""
        try:
            # User indexes
            self.db['users'].create_index('email', unique=True)
            self.db['users'].create_index('created_at')
            
            # Chat indexes
            self.db['chats'].create_index('user_id')
            self.db['chats'].create_index([('user_id', 1), ('created_at', -1)])
            self.db['chats'].create_index('is_deleted')
            
            # Note indexes
            self.db['notes'].create_index('teacher_id')
            self.db['notes'].create_index('subject')
            self.db['notes'].create_index('is_published')
            
            # Assessment indexes
            self.db['assessments'].create_index('teacher_id')
            self.db['assessments'].create_index('is_published')
            
            # Progress indexes
            self.db['progress'].create_index('student_id', unique=True)
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("MongoDB disconnected")
    
    def get_db(self):
        """Get database instance"""
        return self.db
    
    def drop_database(self):
        """Drop entire database (use with caution)"""
        if self.client:
            self.client.drop_database(Config.MONGODB_DB_NAME)
            logger.warning("Database dropped")

db = Database()
