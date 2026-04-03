from datetime import datetime
from bson.objectid import ObjectId
from app.db import db

class Note:
    """Note/Document model for uploaded learning materials"""
    
    def __init__(self, title, content, teacher_id, file_type='text', **kwargs):
        # Store _id as string for consistency
        _id_val = kwargs.get('_id')
        self._id = str(_id_val) if _id_val else str(ObjectId())
        self.title = title
        self.content = content
        # Store teacher_id as string for consistency
        self.teacher_id = str(teacher_id)
        self.file_type = file_type  # 'pdf', 'docx', 'txt', 'text'
        self.subject = kwargs.get('subject', '')
        self.topic = kwargs.get('topic', '')
        self.description = kwargs.get('description', '')
        self.file_path = kwargs.get('file_path', '')
        self.embeddings_stored = kwargs.get('embeddings_stored', False)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        self.is_published = kwargs.get('is_published', True)
        self.metadata = kwargs.get('metadata', {})
    
    def to_dict(self):
        """Convert note to dictionary"""
        return {
            '_id': str(self._id),
            'title': self.title,
            'content': self.content,
            'teacher_id': str(self.teacher_id),
            'file_type': self.file_type,
            'subject': self.subject,
            'topic': self.topic,
            'description': self.description,
            'file_path': self.file_path,
            'embeddings_stored': self.embeddings_stored,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            'is_published': self.is_published,
            'metadata': self.metadata
        }
    
    def save(self):
        """Save note to database"""
        note_collection = db.db['notes']
        note_data = self.to_dict()
        
        # Convert _id to string for storage consistency
        _id_str = str(self._id)
        note_data['_id'] = _id_str
        
        # Check if document exists by querying with string ID
        existing = note_collection.find_one({'_id': _id_str})
        if existing is None:
            # Insert new document with string ID
            note_collection.insert_one(note_data)
        else:
            # Update existing document
            note_collection.update_one(
                {'_id': _id_str},
                {'$set': note_data}
            )
        return _id_str
    
    @staticmethod
    def find_by_id(note_id):
        """Find note by ID"""
        note_collection = db.db['notes']
        # _id is stored as string in MongoDB, query with string format
        note_data = note_collection.find_one({'_id': str(note_id)})
        if note_data:
            return Note(**note_data)
        return None
    
    @staticmethod
    def find_by_teacher(teacher_id):
        """Find all notes by teacher"""
        note_collection = db.db['notes']
        # teacher_id is stored as string in MongoDB, query with string format
        notes = note_collection.find(
            {'teacher_id': str(teacher_id), 'is_published': True}
        ).sort('created_at', -1)
        
        return [Note(**note) for note in notes]
    
    @staticmethod
    def search_by_subject(subject):
        """Search notes by subject"""
        note_collection = db.db['notes']
        notes = note_collection.find(
            {'subject': subject, 'is_published': True}
        ).sort('updated_at', -1)
        
        return [Note(**note) for note in notes]
    
    def mark_embeddings_stored(self):
        """Mark embeddings as stored"""
        note_collection = db.db['notes']
        # Query and update using string ID format
        note_collection.update_one(
            {'_id': str(self._id)},
            {'$set': {'embeddings_stored': True, 'updated_at': datetime.utcnow()}}
        )
        self.embeddings_stored = True
