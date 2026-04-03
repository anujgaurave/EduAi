#!/usr/bin/env python
"""
Debug script to check if backend is properly configured
Run this to verify routes are registered correctly
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def check_backend():
    """Check if backend is properly configured"""
    print("=" * 60)
    print("EduAI Backend Diagnostic")
    print("=" * 60)
    print()
    
    # 1. Check Python version
    print("1. Python Version")
    print(f"   Python {sys.version}")
    print()
    
    # 2. Check imports
    print("2. Checking Imports...")
    try:
        from app import create_app
        print("   ✓ Flask app can be imported")
    except Exception as e:
        print(f"   ✗ Error importing Flask app: {e}")
        return False
    
    try:
        from app.db import db
        print("   ✓ Database module can be imported")
    except Exception as e:
        print(f"   ✗ Error importing database: {e}")
        return False
    
    try:
        from app.routes.auth import auth_bp
        print("   ✓ Auth routes can be imported")
    except Exception as e:
        print(f"   ✗ Error importing auth routes: {e}")
        return False
    
    try:
        from app.routes.chat import chat_bp
        print("   ✓ Chat routes can be imported")
    except Exception as e:
        print(f"   ✗ Error importing chat routes: {e}")
        return False
    
    print()
    
    # 3. Try to create app
    print("3. Creating Flask App...")
    try:
        app = create_app('development')
        print("   ✓ Flask app created successfully")
    except Exception as e:
        print(f"   ✗ Error creating Flask app: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # 4. Check registered routes
    print("4. Registered Routes:")
    print("   Looking for /api/auth and /api/chat routes...")
    print()
    
    with app.app_context():
        routes = []
        for rule in app.url_map.iter_rules():
            if '/api/' in str(rule):
                routes.append(str(rule))
        
        if not routes:
            print("   ✗ NO API ROUTES FOUND!")
            print()
            print("   All routes:")
            for rule in app.url_map.iter_rules():
                print(f"     {rule}")
            return False
        
        auth_routes = [r for r in routes if '/api/auth' in r]
        chat_routes = [r for r in routes if '/api/chat' in r]
        
        if auth_routes:
            print("   ✓ Auth routes found:")
            for route in auth_routes:
                print(f"     {route}")
        else:
            print("   ✗ NO AUTH ROUTES FOUND!")
        
        if chat_routes:
            print("   ✓ Chat routes found:")
            for route in chat_routes:
                print(f"     {route}")
        else:
            print("   ✗ NO CHAT ROUTES FOUND!")
    
    print()
    print("=" * 60)
    
    if auth_routes and chat_routes:
        print("✅ Backend is properly configured!")
        print()
        print("Routes are registered. If you still see 404 errors:")
        print("1. Make sure backend is running: python run.py")
        print("2. Check backend logs for errors")
        print("3. Verify MongoDB is connected")
        return True
    else:
        print("❌ Backend has configuration issues!")
        print()
        print("Missing routes. Check:")
        print("1. Are all route files present?")
        print("2. Are there import errors in route files?")
        print("3. Is the app being created correctly?")
        return False


if __name__ == '__main__':
    success = check_backend()
    sys.exit(0 if success else 1)
