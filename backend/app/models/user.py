from datetime import datetime
from bson.objectid import ObjectId
import bcrypt
import logging
from app.db import db

logger = logging.getLogger(__name__)

class User:
    """User model for authentication and profile management"""
    
    def __init__(self, email, name=None, role='student', password=None, password_hash=None, **kwargs):
        self.email = email
        self.name = name
        self.role = role  # 'student' or 'teacher'
        
        # Handle both new user (with password) and loaded user (with password_hash)
        if password:
            self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        elif password_hash:
            self.password_hash = password_hash
        else:
            self.password_hash = None
        
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        self.is_active = kwargs.get('is_active', True)
        self.profile = {
            'bio': kwargs.get('bio', ''),
            'avatar': kwargs.get('avatar', ''),
            'phone': kwargs.get('phone', ''),
            'institution': kwargs.get('institution', '')
        }
        self._id = kwargs.get('_id', ObjectId())
    
    def verify_password(self, password):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)
    
    def to_dict(self, include_password=False):
        """Convert user to dictionary"""
        user_dict = {
            '_id': str(self._id),
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            'is_active': self.is_active,
            'profile': self.profile
        }
        if include_password:
            user_dict['password_hash'] = self.password_hash
        return user_dict
    
    def save(self):
        """Save user to database"""
        user_collection = db.db['users']
        user_data = self.to_dict(include_password=True)
        result = user_collection.insert_one(user_data)
        self._id = result.inserted_id
        return self._id
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        user_collection = db.db['users']
        user_data = user_collection.find_one({'email': email})
        if user_data:
            return User(**user_data)
        return None
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        import logging
        logger = logging.getLogger(__name__)
        try:
            user_collection = db.db['users']
            
            # Try ObjectId first (standard MongoDB _id format)
            try:
                user_data = user_collection.find_one({'_id': ObjectId(user_id)})
                if user_data:
                    return User(**user_data)
            except Exception:
                pass
            
            # Fallback: try string _id (legacy support)
            user_data = user_collection.find_one({'_id': str(user_id)})
            if user_data:
                return User(**user_data)
            
            logger.warning(f"User not found with id: {user_id}")
            return None
        except Exception as e:
            logger.error(f"Error finding user by id: {e}")
            return None
    
    def update_profile(self, **kwargs):
        """Update user profile"""
        user_collection = db.db['users']
        update_data = {
            'profile': {**self.profile, **kwargs.get('profile', {})},
            'updated_at': datetime.utcnow()
        }
        user_collection.update_one(
            {'_id': self._id},
            {'$set': update_data}
        )
        self.updated_at = update_data['updated_at']
        self.profile = update_data['profile']
    
    def deactivate(self):
        """Deactivate user account"""
        user_collection = db.db['users']
        user_collection.update_one(
            {'_id': self._id},
            {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}}
        )
        self.is_active = False
