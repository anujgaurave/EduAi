from datetime import datetime
from bson.objectid import ObjectId
from app.db import db

class Progress:
    """Student progress tracking model"""
    
    def __init__(self, student_id, **kwargs):
        # Store _id as string for consistency
        _id_val = kwargs.get('_id')
        self._id = str(_id_val) if _id_val else str(ObjectId())
        # Store student_id as string for consistency
        self.student_id = str(student_id)
        self.subjects_completed = kwargs.get('subjects_completed', {})
        self.total_questions_answered = kwargs.get('total_questions_answered', 0)
        self.correct_answers = kwargs.get('correct_answers', 0)
        self.average_score = kwargs.get('average_score', 0.0)
        self.assessments_taken = kwargs.get('assessments_taken', [])
        self.chat_count = kwargs.get('chat_count', 0)
        self.last_activity = kwargs.get('last_activity', datetime.utcnow())
        self.learning_streak = kwargs.get('learning_streak', 0)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    def to_dict(self):
        """Convert progress to dictionary"""
        return {
            '_id': str(self._id),
            'student_id': str(self.student_id),
            'subjects_completed': self.subjects_completed,
            'total_questions_answered': self.total_questions_answered,
            'correct_answers': self.correct_answers,
            'average_score': self.average_score,
            'assessments_taken': [str(a) if isinstance(a, ObjectId) else a for a in self.assessments_taken],
            'chat_count': self.chat_count,
            'last_activity': self.last_activity.isoformat() if isinstance(self.last_activity, datetime) else self.last_activity,
            'learning_streak': self.learning_streak,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    def save(self):
        """Save progress to database"""
        progress_collection = db.db['progress']
        progress_data = self.to_dict()
        
        # Convert _id to string for storage consistency
        _id_str = str(self._id)
        progress_data['_id'] = _id_str
        
        # Check if document exists by querying with string ID
        existing = progress_collection.find_one({'_id': _id_str})
        if existing is None:
            # Insert new document with string ID
            progress_collection.insert_one(progress_data)
        else:
            # Update existing document
            progress_collection.update_one(
                {'_id': _id_str},
                {'$set': progress_data}
            )
        return _id_str
    
    @staticmethod
    def find_by_student(student_id):
        """Find progress for a student"""
        progress_collection = db.db['progress']
        # student_id is stored as string in MongoDB, query with string format
        progress_data = progress_collection.find_one({'student_id': str(student_id)})
        if progress_data:
            return Progress(**progress_data)
        return None
    
    def update_score(self, correct, total):
        """Update student score"""
        progress_collection = db.db['progress']
        self.total_questions_answered += total
        self.correct_answers += correct
        self.average_score = (self.correct_answers / self.total_questions_answered * 100) if self.total_questions_answered > 0 else 0
        self.updated_at = datetime.utcnow()
        
        # Query and update using string ID format
        progress_collection.update_one(
            {'_id': str(self._id)},
            {'$set': self.to_dict()}
        )
        
    def update_activity(self):
        """Update last activity and calculate learning streak"""
        now = datetime.utcnow()
        if self.last_activity:
            if isinstance(self.last_activity, str):
                try:
                    last_date = datetime.fromisoformat(self.last_activity).date()
                except:
                    last_date = now.date()
            else:
                last_date = self.last_activity.date()
                
            delta = now.date() - last_date
            if delta.days == 1:
                self.learning_streak += 1
            elif delta.days > 1:
                self.learning_streak = 1
            # If 0 (same day), maintain streak
        else:
            self.learning_streak = 1
            
        self.last_activity = now
        self.updated_at = now
        
        db.db['progress'].update_one(
            {'_id': str(self._id)},
            {'$set': {'learning_streak': self.learning_streak, 'last_activity': self.last_activity.isoformat()}}
        )
    
    def add_assessment(self, assessment_id, score):
        """Record completed assessment"""
        progress_collection = db.db['progress']
        self.assessments_taken.append({
            'assessment_id': str(assessment_id),
            'score': score,
            'date': datetime.utcnow()
        })
        self.updated_at = datetime.utcnow()
        
        # Query and update using string ID format
        progress_collection.update_one(
            {'_id': str(self._id)},
            {'$push': {'assessments_taken': self.assessments_taken[-1]}}
        )
