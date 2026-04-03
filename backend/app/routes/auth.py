from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
from app.utils.helpers import (
    validate_email, validate_required_fields, sanitize_input, require_role
)
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User signup endpoint"""
    try:
        data = request.get_json()
        
        # Validate input
        is_valid, error = validate_required_fields(
            data, ['email', 'password', 'name', 'role']
        )
        if not is_valid:
            return jsonify({'error': error}), 400
        
        email = sanitize_input(data['email'].strip().lower())
        password = data['password']
        name = sanitize_input(data['name'])
        role = sanitize_input(data['role']).lower()
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        # Validate role
        if role not in ['student', 'teacher']:
            return jsonify({'error': 'Invalid role. Must be student or teacher'}), 400
        
        # Check if user exists
        if User.find_by_email(email):
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create user
        user = User(
            email=email,
            password=password,
            name=name,
            role=role,
            bio=sanitize_input(data.get('bio', '')),
            institution=sanitize_input(data.get('institution', ''))
        )
        
        user_id = user.save()
        
        # Generate token
        access_token = create_access_token(identity=str(user_id))
        
        return jsonify({
            'message': 'Signup successful',
            'user': {
                '_id': str(user_id),
                'email': user.email,
                'name': user.name,
                'role': user.role
            },
            'access_token': access_token
        }), 201
    
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return jsonify({'error': 'Signup failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        # Validate input
        is_valid, error = validate_required_fields(data, ['email', 'password'])
        if not is_valid:
            return jsonify({'error': error}), 400
        
        email = sanitize_input(data['email'].strip().lower())
        password = data['password']
        
        # Find user
        user = User.find_by_email(email)
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify password
        if not user.verify_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if user is active
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Generate token
        access_token = create_access_token(identity=str(user._id))
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                '_id': str(user._id),
                'email': user.email,
                'name': user.name,
                'role': user.role
            },
            'access_token': access_token
        }), 200
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        user_id = get_jwt_identity()
        logger.info(f"Getting profile for user_id: {user_id}")
        
        user = User.find_by_id(user_id)
        
        if not user:
            logger.error(f"User not found for id: {user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Profile fetch error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Could not fetch profile'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        profile_updates = {}
        allowed_fields = ['bio', 'avatar', 'phone', 'institution']
        
        for field in allowed_fields:
            if field in data:
                profile_updates[field] = sanitize_input(data[field])
        
        if profile_updates:
            user.update_profile(profile=profile_updates)
        
        return jsonify({
            'message': 'Profile updated',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        return jsonify({'error': 'Could not update profile'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate input
        is_valid, error = validate_required_fields(
            data, ['old_password', 'new_password']
        )
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Verify old password
        if not user.verify_password(data['old_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Validate new password
        if len(data['new_password']) < 8:
            return jsonify({'error': 'New password must be at least 8 characters'}), 400
        
        if data['new_password'] == data['old_password']:
            return jsonify({'error': 'New password must be different'}), 400
        
        # Update password
        user.password_hash = user.password_hash.__class__(
            data['new_password'].encode('utf-8'),
            user.password_hash.__class__.gensalt()
        )
        
        import bcrypt
        user.password_hash = bcrypt.hashpw(
            data['new_password'].encode('utf-8'),
            bcrypt.gensalt()
        )
        
        from app.db import db
        user_collection = db.db['users']
        user_collection.update_one(
            {'_id': user._id},
            {'$set': {'password_hash': user.password_hash}}
        )
        
        return jsonify({'message': 'Password changed successfully'}), 200
    
    except Exception as e:
        logger.error(f"Password change error: {e}")
        return jsonify({'error': 'Could not change password'}), 500

@auth_bp.route('/deactivate', methods=['POST'])
@jwt_required()
def deactivate_account():
    """Deactivate user account"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.deactivate()
        
        return jsonify({'message': 'Account deactivated'}), 200
    
    except Exception as e:
        logger.error(f"Account deactivation error: {e}")
        return jsonify({'error': 'Could not deactivate account'}), 500
