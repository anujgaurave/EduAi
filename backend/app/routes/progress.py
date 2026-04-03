from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.progress import Progress
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

progress_bp = Blueprint('progress', __name__, url_prefix='/api/progress')

@progress_bp.route('/my-progress', methods=['GET'])
@jwt_required()
def get_my_progress():
    """Get current user's progress"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user or user.role != 'student':
            return jsonify({'error': 'Only students have progress tracking'}), 403
        
        progress = Progress.find_by_student(user_id)
        
        if not progress:
            # Create new progress for student
            progress = Progress(user_id)
            progress.save()
        
        return jsonify({
            'progress': progress.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching progress: {e}")
        return jsonify({'error': 'Could not fetch progress'}), 500

@progress_bp.route('/student/<student_id>', methods=['GET'])
@jwt_required()
def get_student_progress(student_id):
    """Get student's progress (teacher only)"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user or user.role != 'teacher':
            return jsonify({'error': 'Only teachers can view student progress'}), 403
        
        progress = Progress.find_by_student(student_id)
        
        if not progress:
            return jsonify({'error': 'Student not found'}), 404
        
        return jsonify({
            'progress': progress.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching student progress: {e}")
        return jsonify({'error': 'Could not fetch progress'}), 500

@progress_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_progress_stats():
    """Get progress statistics"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user or user.role != 'student':
            return jsonify({'error': 'Only students have progress stats'}), 403
        
        progress = Progress.find_by_student(user_id)
        
        if not progress:
            progress = Progress(user_id)
            progress.save()
        
        # Calculate stats
        total_assessments = len(progress.assessments_taken)
        total_score = sum(a.get('score', 0) for a in progress.assessments_taken) if total_assessments > 0 else 0
        average_score = total_score / total_assessments if total_assessments > 0 else 0
        
        accuracy = (progress.correct_answers / progress.total_questions_answered * 100) if progress.total_questions_answered > 0 else 0
        
        return jsonify({
            'stats': {
                'total_questions_answered': progress.total_questions_answered,
                'correct_answers': progress.correct_answers,
                'accuracy': round(accuracy, 2),
                'total_assessments': total_assessments,
                'average_assessment_score': round(average_score, 2),
                'learning_streak': progress.learning_streak,
                'chat_sessions': progress.chat_count,
                'subjects_completed': progress.subjects_completed
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({'error': 'Could not fetch stats'}), 500

@progress_bp.route('/update-score', methods=['POST'])
@jwt_required()
def update_score():
    """Update student score"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user or user.role != 'student':
            return jsonify({'error': 'Operation not allowed'}), 403
        
        data = request.get_json()
        correct = int(data.get('correct', 0))
        total = int(data.get('total', 1))
        
        progress = Progress.find_by_student(user_id)
        
        if not progress:
            progress = Progress(user_id)
            progress.save()
        
        progress.update_score(correct, total)
        
        return jsonify({
            'message': 'Score updated',
            'progress': progress.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Error updating score: {e}")
        return jsonify({'error': 'Could not update score'}), 500

@progress_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get leaderboard of top students"""
    try:
        limit = int(request.args.get('limit', 10))
        subject = request.args.get('subject', '')
        
        from app.db import db
        
        progress_collection = db.db['progress']
        
        query = {}
        if subject:
            query['subjects_completed'] = {subject: {'$exists': True}}
        
        leaderboard = progress_collection.find(query).sort(
            'average_score', -1
        ).limit(min(limit, 100))
        
        results = []
        for entry in leaderboard:
            student = User.find_by_id(entry['student_id'])
            if student:
                results.append({
                    'student_name': student.name,
                    'average_score': entry['average_score'],
                    'correct_answers': entry['correct_answers'],
                    'total_questions': entry['total_questions_answered']
                })
        
        return jsonify({
            'leaderboard': results
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        return jsonify({'error': 'Could not fetch leaderboard'}), 500
