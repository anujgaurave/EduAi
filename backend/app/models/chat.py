from datetime import datetime
from bson.objectid import ObjectId
from app.db import db

class Chat:
    """Chat session model"""
    
    def __init__(self, user_id, title='New Chat', **kwargs):
        # Store _id as a string for consistency
        _id_val = kwargs.get('_id')
        self._id = str(_id_val) if _id_val else str(ObjectId())
        # Store user_id as string for consistency with MongoDB storage
        self.user_id = str(user_id)
        self.title = title
        self.messages = kwargs.get('messages', [])
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        self.is_deleted = kwargs.get('is_deleted', False)
    
    def add_message(self, role, content, attachments=None):
        """Add message to chat"""
        message = {
            '_id': ObjectId(),
            'role': role,  # 'user' or 'assistant'
            'content': content,
            'attachments': attachments or [],
            'timestamp': datetime.utcnow(),
            'tokens_used': 0
        }
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
        return message
    
    def to_dict(self):
        """Convert chat to dictionary"""
        return {
            '_id': str(self._id),
            'user_id': str(self.user_id),
            'title': self.title,
            'messages': [
                {
                    **msg,
                    '_id': str(msg['_id']),
                    'timestamp': msg['timestamp'].isoformat() if isinstance(msg['timestamp'], datetime) else msg['timestamp']
                }
                for msg in self.messages
            ],
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            'is_deleted': self.is_deleted
        }
    
    def save(self):
        """Save chat to database"""
        chat_collection = db.db['chats']
        chat_data = self.to_dict()
        
        # Convert _id to string for storage consistency
        _id_str = str(self._id)
        chat_data['_id'] = _id_str
        
        # Check if document exists by querying with string ID
        existing = chat_collection.find_one({'_id': _id_str})
        if existing is None:
            # Insert new document with string ID
            chat_collection.insert_one(chat_data)
        else:
            # Update existing document
            chat_collection.update_one(
                {'_id': _id_str},
                {'$set': chat_data}
            )
        return _id_str
    
    @staticmethod
    def find_by_id(chat_id):
        """Find chat by ID"""
        chat_collection = db.db['chats']
        # _id is stored as string in MongoDB, query with string format
        chat_data = chat_collection.find_one({'_id': str(chat_id)})
        if chat_data:
            return Chat(**chat_data)
        return None
    
    @staticmethod
    def find_by_user(user_id, limit=50, skip=0):
        """Find all chats for a user"""
        chat_collection = db.db['chats']
        # user_id is stored as string in MongoDB, query with string format
        chats = chat_collection.find(
            {'user_id': str(user_id), 'is_deleted': False}
        ).sort('updated_at', -1).skip(skip).limit(limit)
        
        return [Chat(**chat) for chat in chats]
    
    def delete_soft(self):
        """Soft delete chat"""
        chat_collection = db.db['chats']
        chat_collection.update_one(
            {'_id': self._id},
            {'$set': {'is_deleted': True, 'updated_at': datetime.utcnow()}}
        )
    
    def get_recent_context(self, num_messages=5):
        """Get recent messages for context"""
        return self.messages[-num_messages:] if len(self.messages) > 0 else []
