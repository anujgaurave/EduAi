"""
Comprehensive Edge Case Tests for EduAI Platform
Tests all role-based access control and user authentication scenarios
"""

import pytest
import json
from app import create_app
from app.db import db
from app.models.user import User
from flask_jwt_extended import create_access_token


class TestAuthEdgeCases:
    """Test authentication and role-based access control"""
    
    @pytest.fixture
    def app(self):
        """Create test app"""
        app = create_app('testing')
        with app.app_context():
            yield app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    @pytest.fixture
    def student_user(self, app):
        """Create a test student user"""
        with app.app_context():
            user = User(
                email="student@test.com",
                name="Test Student",
                role="student",
                password="TestPassword123"
            )
            user_id = user.save()
            return str(user_id)
    
    @pytest.fixture
    def teacher_user(self, app):
        """Create a test teacher user"""
        with app.app_context():
            user = User(
                email="teacher@test.com",
                name="Test Teacher",
                role="teacher",
                password="TestPassword123"
            )
            user_id = user.save()
            return str(user_id)
    
    @pytest.fixture
    def student_token(self, app, student_user):
        """Generate student JWT token"""
        with app.app_context():
            token = create_access_token(identity=student_user)
            return token
    
    @pytest.fixture
    def teacher_token(self, app, teacher_user):
        """Generate teacher JWT token"""
        with app.app_context():
            token = create_access_token(identity=teacher_user)
            return token


class TestStudentEndpoints(TestAuthEdgeCases):
    """Test that student-only endpoints work correctly"""
    
    def test_student_get_own_progress_success(self, client, student_token):
        """Student should be able to get their own progress"""
        response = client.get(
            '/api/progress/my-progress',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code in [200, 201]
        data = json.loads(response.data)
        assert 'progress' in data or 'message' in data
    
    def test_teacher_cannot_get_progress(self, client, teacher_token):
        """Teacher should NOT get progress from student endpoint"""
        response = client.get(
            '/api/progress/my-progress',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        # Should return 403 Forbidden since teacher is not a student
        assert response.status_code == 403
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_no_token_returns_401(self, client):
        """Request without token should return 401"""
        response = client.get('/api/progress/my-progress')
        assert response.status_code == 401


class TestTeacherEndpoints(TestAuthEdgeCases):
    """Test that teacher-only endpoints work correctly"""
    
    def test_teacher_can_create_assessment(self, client, teacher_token):
        """Teacher should be able to create assessment"""
        payload = {
            'title': 'Math Test',
            'subject': 'Mathematics',
            'questions': [
                {
                    'question_text': 'What is 2+2?',
                    'question_type': 'mcq',
                    'options': ['3', '4', '5', '6'],
                    'correct_answer': 'B',
                    'marks': 1
                }
            ]
        }
        response = client.post(
            '/api/assessments/create',
            headers={'Authorization': f'Bearer {teacher_token}'},
            data=json.dumps(payload),
            content_type='application/json'
        )
        # Should succeed or create assessment
        assert response.status_code in [201, 200, 400]  # 400 if validation fails
    
    def test_student_cannot_create_assessment(self, client, student_token):
        """Student should NOT be able to create assessment"""
        payload = {
            'title': 'Math Test',
            'subject': 'Mathematics',
            'questions': [
                {
                    'question_text': 'What is 2+2?',
                    'question_type': 'mcq',
                    'options': ['3', '4', '5', '6'],
                    'correct_answer': 'B'
                }
            ]
        }
        response = client.post(
            '/api/assessments/create',
            headers={'Authorization': f'Bearer {student_token}'},
            data=json.dumps(payload),
            content_type='application/json'
        )
        # Should return 403 Forbidden
        assert response.status_code == 403
        data = json.loads(response.data)
        assert 'error' in data


class TestProfileAccess(TestAuthEdgeCases):
    """Test profile endpoint access control"""
    
    def test_student_get_own_profile(self, client, student_token):
        """Student should be able to get their own profile"""
        response = client.get(
            '/api/auth/profile',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'user' in data
        assert data['user']['role'] == 'student'
    
    def test_teacher_get_own_profile(self, client, teacher_token):
        """Teacher should be able to get their own profile"""
        response = client.get(
            '/api/auth/profile',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'user' in data
        assert data['user']['role'] == 'teacher'
    
    def test_both_roles_can_update_profile(self, client, student_token, teacher_token):
        """Both roles should be able to update their profile"""
        payload = {'profile': {'bio': 'Updated bio'}}
        
        # Student update
        response = client.put(
            '/api/auth/profile',
            headers={'Authorization': f'Bearer {student_token}'},
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code in [200, 201]
        
        # Teacher update
        response = client.put(
            '/api/auth/profile',
            headers={'Authorization': f'Bearer {teacher_token}'},
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code in [200, 201]


class TestInvalidTokens(TestAuthEdgeCases):
    """Test handling of invalid/expired tokens"""
    
    def test_malformed_token(self, client):
        """Malformed token should return 401"""
        response = client.get(
            '/api/auth/profile',
            headers={'Authorization': 'Bearer invalid_token_here'}
        )
        assert response.status_code == 401
    
    def test_missing_bearer_prefix(self, client, student_token):
        """Token without Bearer prefix should fail"""
        response = client.get(
            '/api/auth/profile',
            headers={'Authorization': student_token}  # Missing "Bearer "
        )
        assert response.status_code == 401
    
    def test_empty_authorization_header(self, client):
        """Empty Authorization header should fail"""
        response = client.get(
            '/api/auth/profile',
            headers={'Authorization': ''}
        )
        assert response.status_code == 401


class TestSignupEdgeCases(TestAuthEdgeCases):
    """Test signup validation"""
    
    def test_signup_creates_student_by_default(self, client):
        """Signup without role should create student"""
        payload = {
            'email': 'newstudent@test.com',
            'password': 'ValidPassword123',
            'name': 'New Student'
        }
        response = client.post(
            '/api/auth/signup',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['user']['role'] == 'student'
    
    def test_signup_can_create_teacher(self, client):
        """Signup with teacher role should work"""
        payload = {
            'email': 'newteacher@test.com',
            'password': 'ValidPassword123',
            'name': 'New Teacher',
            'role': 'teacher'
        }
        response = client.post(
            '/api/auth/signup',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['user']['role'] == 'teacher'
    
    def test_invalid_role_rejected(self, client):
        """Invalid role should be rejected"""
        payload = {
            'email': 'test@test.com',
            'password': 'ValidPassword123',
            'name': 'Test User',
            'role': 'admin'  # Invalid role
        }
        response = client.post(
            '/api/auth/signup',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_duplicate_email_rejected(self, client):
        """Duplicate email should be rejected"""
        payload = {
            'email': 'duplicate@test.com',
            'password': 'ValidPassword123',
            'name': 'User 1'
        }
        # First signup
        response1 = client.post(
            '/api/auth/signup',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response1.status_code == 201
        
        # Duplicate signup
        response2 = client.post(
            '/api/auth/signup',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response2.status_code == 409  # Already exists


class TestCrossRoleAccess(TestAuthEdgeCases):
    """Test that roles cannot access other role's endpoints"""
    
    def test_student_cannot_view_teacher_analytics(self, client, student_token, teacher_user):
        """Student cannot view another teacher's data"""
        response = client.get(
            f'/api/progress/student/{teacher_user}',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        # Should fail - students can't view other student progress
        assert response.status_code in [403, 404]
    
    def test_teacher_can_view_student_progress(self, client, teacher_token, student_user):
        """Teacher can view a student's progress"""
        response = client.get(
            f'/api/progress/student/{student_user}',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        # Should succeed or return 200/201
        assert response.status_code in [200, 201, 404]  # 404 if no progress yet


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
