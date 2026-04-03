"""
Pytest configuration and fixtures
"""

import pytest
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.db import db as _db


@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    app = create_app('testing')
    
    with app.app_context():
        # Create test database
        if not _db.db:
            _db.connect()
        
        yield app
        
        # Cleanup
        if _db.db:
            # Drop test database
            _db.client.drop_database(_db.db.name)


@pytest.fixture
def db(app):
    """Create test database."""
    with app.app_context():
        yield _db
        
        # Clear collections after each test
        if _db.db:
            _db.db['users'].delete_many({})
            _db.db['chats'].delete_many({})
            _db.db['notes'].delete_many({})
            _db.db['assessments'].delete_many({})
            _db.db['progress'].delete_many({})
