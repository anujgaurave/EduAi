"""
Test Chat and Notes endpoints with role-based access
"""

import pytest
import json
from flask_jwt_extended import create_access_token
from app.models.user import User


class TestChatEndpoints:
    """Test chat functionality with role validation"""
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def student_user(self, app):
        with app.app_context():
            user = User(
                email=f"student_chat@test.com",
                name="Chat Student",
                role="student",
                password="TestPassword123"
            )
            user_id = user.save()
            return str(user_id)
    
    @pytest.fixture
    def student_token(self, app, student_user):
        with app.app_context():
            return create_access_token(identity=student_user)
    
    def test_student_can_create_chat(self, client, student_token):
        """Student should be able to create chat session"""
        payload = {'title': 'Math Doubts'}
        response = client.post(
            '/api/chat/sessions',
            headers={'Authorization': f'Bearer {student_token}'},
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code in [201, 200]
        data = json.loads(response.data)
        assert 'chat' in data or 'message' in data
    
    def test_student_can_list_chats(self, client, student_token):
        """Student should be able to list their chats"""
        response = client.get(
            '/api/chat/sessions',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'chats' in data
        assert isinstance(data['chats'], list)
    
    def test_chat_requires_authentication(self, client):
        """Chat endpoint should require authentication"""
        response = client.get('/api/chat/sessions')
        assert response.status_code == 401
    
    def test_invalid_token_cannot_access_chat(self, client):
        """Invalid token should not access chat"""
        response = client.get(
            '/api/chat/sessions',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        assert response.status_code == 401


class TestNotesEndpoints:
    """Test notes functionality"""
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def student_user(self, app):
        with app.app_context():
            user = User(
                email=f"student_notes@test.com",
                name="Notes Student",
                role="student",
                password="TestPassword123"
            )
            user_id = user.save()
            return str(user_id)
    
    @pytest.fixture
    def student_token(self, app, student_user):
        with app.app_context():
            return create_access_token(identity=student_user)
    
    def test_student_can_list_notes(self, client, student_token):
        """Student should be able to list notes"""
        response = client.get(
            '/api/notes',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'notes' in data
        assert isinstance(data['notes'], list)
    
    def test_notes_pagination(self, client, student_token):
        """Notes should support pagination"""
        response = client.get(
            '/api/notes?page=1&limit=10',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'page' in data or 'limit' in data
    
    def test_notes_filtering_by_subject(self, client, student_token):
        """Should be able to filter notes by subject"""
        response = client.get(
            '/api/notes?subject=Mathematics',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code == 200
    
    def test_notes_requires_authentication(self, client):
        """Notes endpoint should require authentication"""
        response = client.get('/api/notes')
        assert response.status_code == 401


class TestLeaderboardAccess:
    """Test leaderboard access control"""
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def student_token(self, app):
        with app.app_context():
            user = User(
                email="leaderboard_student@test.com",
                name="Board Student",
                role="student",
                password="TestPassword123"
            )
            user_id = user.save()
            token = create_access_token(identity=str(user_id))
            return token
    
    @pytest.fixture
    def teacher_token(self, app):
        with app.app_context():
            user = User(
                email="leaderboard_teacher@test.com",
                name="Board Teacher",
                role="teacher",
                password="TestPassword123"
            )
            user_id = user.save()
            token = create_access_token(identity=str(user_id))
            return token
    
    def test_student_can_access_leaderboard(self, client, student_token):
        """Student should be able to access leaderboard"""
        response = client.get(
            '/api/progress/leaderboard',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        # Should succeed
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'leaderboard' in data or 'rankings' in data or 'limit' in data
    
    def test_teacher_can_access_leaderboard(self, client, teacher_token):
        """Teacher should be able to access leaderboard"""
        response = client.get(
            '/api/progress/leaderboard',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        assert response.status_code == 200


class TestDataIsoleation:
    """Test that users can only access their own data"""
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def setup_two_students(self, app):
        """Create two student users"""
        with app.app_context():
            student1 = User(
                email="isolation_student1@test.com",
                name="Student 1",
                role="student",
                password="TestPassword123"
            )
            student1_id = student1.save()
            
            student2 = User(
                email="isolation_student2@test.com",
                name="Student 2",
                role="student",
                password="TestPassword123"
            )
            student2_id = student2.save()
            
            token1 = create_access_token(identity=str(student1_id))
            token2 = create_access_token(identity=str(student2_id))
            
            return {
                'student1_id': str(student1_id),
                'student2_id': str(student2_id),
                'token1': token1,
                'token2': token2
            }
    
    def test_student_cannot_see_other_progress(self, client, setup_two_students):
        """Student 1 should NOT see Student 2's progress"""
        student2_id = setup_two_students['student2_id']
        token1 = setup_two_students['token1']
        
        # Try to access student 2's progress with student 1's token
        response = client.get(
            f'/api/progress/student/{student2_id}',
            headers={'Authorization': f'Bearer {token1}'}
        )
        # Should fail - student cannot view other student's data
        assert response.status_code in [403, 404]
    
    def test_student_profile_isolation(self, client, setup_two_students):
        """Each student should only see their own profile"""
        token1 = setup_two_students['token1']
        token2 = setup_two_students['token2']
        
        response1 = client.get(
            '/api/auth/profile',
            headers={'Authorization': f'Bearer {token1}'}
        )
        data1 = json.loads(response1.data)
        
        response2 = client.get(
            '/api/auth/profile',
            headers={'Authorization': f'Bearer {token2}'}
        )
        data2 = json.loads(response2.data)
        
        # Both should succeed but return different users
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert data1['user']['email'] != data2['user']['email']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
