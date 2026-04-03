from datetime import datetime
from bson.objectid import ObjectId
from app.db import db

class Assessment:
    """Assessment/Quiz model"""
    
    def __init__(self, title, questions, teacher_id, **kwargs):
        # Store _id as string for consistency
        _id_val = kwargs.get('_id')
        self._id = str(_id_val) if _id_val else str(ObjectId())
        self.title = title
        self.questions = questions  # List of question IDs
        # Store teacher_id as string for consistency
        self.teacher_id = str(teacher_id)
        self.description = kwargs.get('description', '')
        self.subject = kwargs.get('subject', '')
        self.total_marks = kwargs.get('total_marks', len(questions))
        self.duration_minutes = kwargs.get('duration_minutes', 60)
        self.passing_percentage = kwargs.get('passing_percentage', 40)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        self.is_published = kwargs.get('is_published', False)
        self.show_answers_after = kwargs.get('show_answers_after', True)
    
    def to_dict(self):
        """Convert assessment to dictionary"""
        return {
            '_id': str(self._id),
            'title': self.title,
            'questions': [str(q) if isinstance(q, ObjectId) else q for q in self.questions],
            'teacher_id': str(self.teacher_id),
            'description': self.description,
            'subject': self.subject,
            'total_marks': self.total_marks,
            'duration_minutes': self.duration_minutes,
            'passing_percentage': self.passing_percentage,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            'is_published': self.is_published,
            'show_answers_after': self.show_answers_after
        }
    
    def save(self):
        """Save assessment to database"""
        assessment_collection = db.db['assessments']
        assessment_data = self.to_dict()
        
        # Convert _id to string for storage consistency
        _id_str = str(self._id)
        assessment_data['_id'] = _id_str
        
        # Check if document exists by querying with string ID
        existing = assessment_collection.find_one({'_id': _id_str})
        if existing is None:
            # Insert new document with string ID
            assessment_collection.insert_one(assessment_data)
        else:
            # Update existing document
            assessment_collection.update_one(
                {'_id': _id_str},
                {'$set': assessment_data}
            )
        return _id_str
    
    @staticmethod
    def find_by_id(assessment_id):
        """Find assessment by ID"""
        assessment_collection = db.db['assessments']
        # _id is stored as string in MongoDB, query with string format
        assessment_data = assessment_collection.find_one({'_id': str(assessment_id)})
        if assessment_data:
            return Assessment(**assessment_data)
        return None
    
    @staticmethod
    def find_by_teacher(teacher_id):
        """Find all assessments by teacher"""
        assessment_collection = db.db['assessments']
        # teacher_id is stored as string in MongoDB, query with string format
        assessments = assessment_collection.find(
            {'teacher_id': str(teacher_id)}
        ).sort('created_at', -1)
        
        return [Assessment(**assessment) for assessment in assessments]
    
    def publish(self):
        """Publish assessment"""
        assessment_collection = db.db['assessments']
        # Query and update using string ID format
        assessment_collection.update_one(
            {'_id': str(self._id)},
            {'$set': {'is_published': True, 'updated_at': datetime.utcnow()}}
        )
        self.is_published = True

class Question:
    """Question model for assessments"""
    
    def __init__(self, question_text, question_type, options, correct_answer, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.question_text = question_text
        self.question_type = question_type  # 'mcq', 'short_answer', 'essay'
        self.options = options  # List of options for MCQ
        self.correct_answer = correct_answer
        self.marks = kwargs.get('marks', 1)
        self.explanation = kwargs.get('explanation', '')
        self.subject = kwargs.get('subject', '')
        self.difficulty = kwargs.get('difficulty', 'medium')  # 'easy', 'medium', 'hard'
        self.created_at = kwargs.get('created_at', datetime.utcnow())
    
    def to_dict(self):
        """Convert question to dictionary"""
        return {
            '_id': str(self._id),
            'question_text': self.question_text,
            'question_type': self.question_type,
            'options': self.options,
            'correct_answer': self.correct_answer,
            'marks': self.marks,
            'explanation': self.explanation,
            'subject': self.subject,
            'difficulty': self.difficulty,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    def save(self):
        """Save question to database"""
        question_collection = db.db['questions']
        question_data = self.to_dict()
        
        result = question_collection.insert_one(question_data)
        self._id = result.inserted_id
        return self._id
