from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.assessment import Assessment, Question
from app.models.user import User
from app.models.progress import Progress
from app.utils.helpers import sanitize_input, validate_required_fields, require_role
from app.services.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)

assessments_bp = Blueprint('assessments', __name__, url_prefix='/api/assessments')

@assessments_bp.route('/create', methods=['POST'])
@jwt_required()
def create_assessment():
    """Create assessment (teacher only)"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user or user.role != 'teacher':
            return jsonify({'error': 'Only teachers can create assessments'}), 403
        
        data = request.get_json()
        
        # Validate input
        is_valid, error = validate_required_fields(
            data, ['title', 'subject', 'questions']
        )
        if not is_valid:
            return jsonify({'error': error}), 400
        
        title = sanitize_input(data['title'])
        subject = sanitize_input(data['subject'])
        questions = data['questions']
        
        if not isinstance(questions, list) or len(questions) == 0:
            return jsonify({'error': 'At least one question required'}), 400
        
        # Create questions
        question_ids = []
        for q in questions:
            question = Question(
                question_text=sanitize_input(q['question_text']),
                question_type=q.get('question_type', 'mcq'),
                options=q.get('options', []),
                correct_answer=q.get('correct_answer'),
                marks=q.get('marks', 1),
                explanation=sanitize_input(q.get('explanation', ''))
            )
            question_id = question.save()
            question_ids.append(question_id)
        
        # Create assessment
        assessment = Assessment(
            title=title,
            questions=question_ids,
            teacher_id=user_id,
            subject=subject,
            description=sanitize_input(data.get('description', '')),
            total_marks=sum(int(q.get('marks', 1)) for q in questions),
            duration_minutes=int(data.get('duration_minutes', 60)),
            passing_percentage=int(data.get('passing_percentage', 40))
        )
        
        assessment_id = assessment.save()
        
        return jsonify({
            'message': 'Assessment created',
            'assessment': assessment.to_dict()
        }), 201
    
    except Exception as e:
        logger.error(f"Error creating assessment: {e}")
        return jsonify({'error': 'Could not create assessment'}), 500

@assessments_bp.route('/<assessment_id>', methods=['GET'])
@jwt_required()
def get_assessment(assessment_id):
    """Get assessment details"""
    try:
        user_id = get_jwt_identity()
        
        assessment = Assessment.find_by_id(assessment_id)
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
        
        user = User.find_by_id(user_id)
        
        # Students can only see published assessments
        if user.role == 'student' and not assessment.is_published:
            return jsonify({'error': 'Assessment not available'}), 403
        
        # Teachers can see their own assessments
        if user.role == 'teacher' and str(assessment.teacher_id) != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        assessment_data = assessment.to_dict()
        
        # Load questions
        from app.db import db
        from bson.objectid import ObjectId
        
        question_collection = db.db['questions']
        questions = []
        for q_id in assessment.questions:
            # Query by string first
            q_data = question_collection.find_one({'_id': str(q_id)})
            
            # Fallback for old questions using ObjectId
            if not q_data:
                try:
                    q_data = question_collection.find_one({'_id': ObjectId(str(q_id))})
                except Exception:
                    pass
                    
            if q_data:
                questions.append(q_data)
        
        assessment_data['questions'] = questions
        
        return jsonify({
            'assessment': assessment_data
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching assessment: {e}")
        return jsonify({'error': 'Could not fetch assessment'}), 500

@assessments_bp.route('/publish/<assessment_id>', methods=['POST'])
@jwt_required()
def publish_assessment(assessment_id):
    """Publish assessment (teacher only)"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user or user.role != 'teacher':
            return jsonify({'error': 'Only teachers can publish assessments'}), 403
        
        assessment = Assessment.find_by_id(assessment_id)
        
        if not assessment or str(assessment.teacher_id) != user_id:
            return jsonify({'error': 'Assessment not found'}), 404
        
        assessment.publish()
        
        return jsonify({
            'message': 'Assessment published',
            'assessment': assessment.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Error publishing assessment: {e}")
        return jsonify({'error': 'Could not publish assessment'}), 500

@assessments_bp.route('/submit/<assessment_id>', methods=['POST'])
@jwt_required()
def submit_assessment(assessment_id):
    """Submit assessment answers"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user or user.role != 'student':
            return jsonify({'error': 'Only students can submit assessments'}), 403
        
        assessment = Assessment.find_by_id(assessment_id)
        
        if not assessment or not assessment.is_published:
            return jsonify({'error': 'Assessment not available'}), 404
        
        data = request.get_json()
        answers = data.get('answers', {})  # {question_id: answer}
        
        if not answers:
            return jsonify({'error': 'No answers provided'}), 400
        
        # Check for retakes before grading
        progress = Progress.find_by_student(user_id)
        if progress:
            for a in progress.assessments_taken:
                if a.get('assessment_id') == assessment_id:
                    return jsonify({'error': 'You have already taken this assessment'}), 400
        
        # Calculate score
        from app.db import db
        from bson.objectid import ObjectId
        
        question_collection = db.db['questions']
        correct_count = 0
        total_marks = 0
        correct_q_count = 0
        total_q_count = 0
        
        for q_id, student_answer in answers.items():
            q_data = question_collection.find_one({'_id': str(q_id)})
            if not q_data:
                try:
                    q_data = question_collection.find_one({'_id': ObjectId(str(q_id))})
                except Exception:
                    pass
            
            if q_data:
                total_marks += q_data.get('marks', 1)
                total_q_count += 1
                if str(q_data.get('correct_answer')).lower() == str(student_answer).lower():
                    correct_count += q_data.get('marks', 1)
                    correct_q_count += 1
        
        score = (correct_count / total_marks * 100) if total_marks > 0 else 0
        passed = score >= assessment.passing_percentage
        
        # Update progress
        progress = Progress.find_by_student(user_id)
        if not progress:
            progress = Progress(user_id)
            progress.save()
            
        progress.update_score(correct_q_count, total_q_count)
        
        progress.update_activity()
        progress.add_assessment(assessment_id, score)
        
        return jsonify({
            'message': 'Assessment submitted',
            'score': round(score, 2),
            'total_marks': total_marks,
            'correct_answers': correct_count,
            'passed': passed,
            'passing_percentage': assessment.passing_percentage
        }), 200
    
    except Exception as e:
        logger.error(f"Error submitting assessment: {e}")
        return jsonify({'error': 'Could not submit assessment'}), 500

@assessments_bp.route('/generate-quiz', methods=['POST'])
@jwt_required()
def generate_quiz():
    """Generate quiz using AI"""
    try:
        user_id = get_jwt_identity()
        
        data = request.get_json()
        
        is_valid, error = validate_required_fields(data, ['topic'])
        if not is_valid:
            return jsonify({'error': error}), 400
        
        topic = sanitize_input(data['topic'])
        num_questions = int(data.get('num_questions', 5))
        difficulty = sanitize_input(data.get('difficulty', 'medium'))
        
        # Generate quiz
        result = ai_service.generate_quiz(topic, num_questions, difficulty)
        
        return jsonify(result), 200 if result.get('success') else 500
    
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        return jsonify({'error': 'Could not generate quiz'}), 500

@assessments_bp.route('/available', methods=['GET'])
@jwt_required()
def get_available_assessments():
    """Get available assessments for student"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user or user.role != 'student':
            return jsonify({'error': 'Only students can access this'}), 403
        
        from app.db import db
        
        assessment_collection = db.db['assessments']
        assessments = assessment_collection.find(
            {'is_published': True}
        ).sort('created_at', -1)
        
        # Check student progress
        user_id = get_jwt_identity()
        progress_collection = db.db['progress']
        progress = progress_collection.find_one({'student_id': str(user_id)})
        taken_ids = [a.get('assessment_id') for a in progress.get('assessments_taken', [])] if progress else []
        
        result = []
        for a in assessments:
            assessment_data = Assessment(**a).to_dict()
            assessment_data['is_completed'] = str(assessment_data['_id']) in taken_ids
            result.append(assessment_data)
        
        return jsonify({'assessments': result}), 200
    
    except Exception as e:
        logger.error(f"Error fetching available assessments: {e}")
        return jsonify({'error': 'Could not fetch assessments'}), 500

@assessments_bp.route('/my-assessments', methods=['GET'])
@jwt_required()
def get_teacher_assessments():
    """Get all assessments created by this teacher"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user or user.role != 'teacher':
            return jsonify({'error': 'Only teachers can access this'}), 403
        
        from app.db import db
        from bson.objectid import ObjectId
        
        assessment_collection = db.db['assessments']
        # Find by teacher_id (stored as string)
        assessments_cursor = assessment_collection.find(
            {'teacher_id': str(user_id)}
        ).sort('created_at', -1)
        
        result = []
        for a in assessments_cursor:
            assessment = Assessment(**a)
            a_dict = assessment.to_dict()
            
            question_collection = db.db['questions']
            questions = []
            for q_id in assessment.questions:
                q_data = question_collection.find_one({'_id': str(q_id)})
                if not q_data:
                    try:
                        q_data = question_collection.find_one({'_id': ObjectId(str(q_id))})
                    except Exception:
                        pass
                if q_data:
                    questions.append(q_data)
            a_dict['questions'] = questions
            result.append(a_dict)
        
        return jsonify({'assessments': result}), 200
    
    except Exception as e:
        logger.error(f"Error fetching teacher assessments: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Could not fetch assessments'}), 500

@assessments_bp.route('/<assessment_id>/submissions', methods=['GET'])
@jwt_required()
def get_assessment_submissions(assessment_id):
    """Get all submissions for an assessment (teacher only)"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user or user.role != 'teacher':
            return jsonify({'error': 'Only teachers can access submissions'}), 403
            
        assessment = Assessment.find_by_id(assessment_id)
        if not assessment or str(assessment.teacher_id) != str(user_id):
            return jsonify({'error': 'Assessment not found or unauthorized'}), 404
            
        from app.db import db
        from bson.objectid import ObjectId
        progress_collection = db.db['progress']
        users_collection = db.db['users']
        
        # Find all progress documents that have this assessment in their assessments_taken array
        progress_docs = progress_collection.find({
            'assessments_taken.assessment_id': str(assessment_id)
        })
        
        submissions = []
        for p in progress_docs:
            # Get specific assessment element
            taken_data = next((a for a in p.get('assessments_taken', []) if a.get('assessment_id') == str(assessment_id)), None)
            if not taken_data: continue
            
            # Fetch student info
            student = users_collection.find_one({'_id': ObjectId(p['student_id']) if p['student_id'] and len(p['student_id']) == 24 else p['student_id']})
            student_name = student.get('name', 'Unknown') if student else 'Unknown'
            student_email = student.get('email', 'Unknown') if student else 'Unknown'
            
            submissions.append({
                'student_id': p['student_id'],
                'student_name': student_name,
                'student_email': student_email,
                'score': taken_data.get('score', 0),
                'date': taken_data.get('date'),
                'passed': taken_data.get('score', 0) >= assessment.passing_percentage
            })
            
        return jsonify({'submissions': submissions}), 200

    except Exception as e:
        logger.error(f"Error fetching submissions: {e}")
        return jsonify({'error': 'Could not fetch submissions'}), 500

@assessments_bp.route('/<assessment_id>', methods=['PUT'])
@jwt_required()
def edit_assessment(assessment_id):
    """Edit an existing assessment (teacher only)"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user or user.role != 'teacher':
            return jsonify({'error': 'Only teachers can edit assessments'}), 403
            
        assessment = Assessment.find_by_id(assessment_id)
        if not assessment or str(assessment.teacher_id) != str(user_id):
            return jsonify({'error': 'Assessment not found or unauthorized'}), 404
            
        data = request.get_json()
        
        is_valid, error = validate_required_fields(data, ['title', 'subject'])
        if not is_valid:
            return jsonify({'error': error}), 400
            
        assessment.title = sanitize_input(data['title'])
        assessment.subject = sanitize_input(data['subject'])
        assessment.description = sanitize_input(data.get('description', ''))
        assessment.duration_minutes = data.get('duration_minutes', assessment.duration_minutes)
        assessment.passing_percentage = data.get('passing_percentage', assessment.passing_percentage)
        
        # Optionally handle questions replacement if provided
        if 'questions' in data and isinstance(data['questions'], list) and len(data['questions']) > 0:
            question_ids = []
            for q in data['questions']:
                # If question has existing _id and isn't a new local state question string, we could keep it, 
                # but simplest is saving new objects or overwriting.
                # Since the UI creates new questions every time on save, we generate new ones.
                question = Question(
                    question_text=sanitize_input(q.get('question_text', '')),
                    question_type=q.get('question_type', 'mcq'),
                    options=q.get('options', []),
                    correct_answer=q.get('correct_answer'),
                    marks=q.get('marks', 1),
                    explanation=sanitize_input(q.get('explanation', ''))
                )
                question_ids.append(question.save())
            assessment.questions = question_ids
            assessment.total_marks = sum([q.get('marks', 1) for q in data['questions']])
        
        assessment.save()
        return jsonify({'message': 'Assessment updated successfully', 'assessment': assessment.to_dict()}), 200

    except Exception as e:
        logger.error(f"Error editing assessment: {e}")
        return jsonify({'error': 'Could not update assessment'}), 500

@assessments_bp.route('/<assessment_id>/submissions/<student_id>', methods=['DELETE'])
@jwt_required()
def allow_reattempt(assessment_id, student_id):
    """Allow a student to reattempt an assessment by deleting their progress (teacher only)"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user or user.role != 'teacher':
            return jsonify({'error': 'Only teachers can allow reattempts'}), 403
            
        assessment = Assessment.find_by_id(assessment_id)
        if not assessment or str(assessment.teacher_id) != str(user_id):
            return jsonify({'error': 'Assessment not found or unauthorized'}), 404
            
        from app.db import db
        progress_collection = db.db['progress']
        
        # Pull the specific assessment from the assessments_taken array for this student
        result = progress_collection.update_one(
            {'student_id': str(student_id)},
            {'$pull': {'assessments_taken': {'assessment_id': str(assessment_id)}}}
        )
        
        if result.modified_count > 0:
            return jsonify({'message': 'Reattempt allowed successfully'}), 200
        else:
            return jsonify({'error': 'Submission not found or already deleted'}), 404

    except Exception as e:
        logger.error(f"Error allowing reattempt: {e}")
        return jsonify({'error': 'Could not allow reattempt'}), 500
