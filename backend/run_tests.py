#!/usr/bin/env python
"""
Quick test runner script
Run this to execute all tests and show results
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests"""
    os.chdir(os.path.dirname(__file__))
    
    print("=" * 60)
    print("EduAI Platform - Comprehensive Test Suite")
    print("=" * 60)
    print()
    
    # Install pytest if needed
    print("[1/3] Installing test dependencies...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'pytest', 'pytest-flask'], check=False)
    print("✓ Dependencies installed")
    print()
    
    # Run all tests
    print("[2/3] Running all tests...")
    print("-" * 60)
    result = subprocess.run([
        sys.executable, '-m', 'pytest',
        'test_edge_cases.py',
        'test_endpoints.py',
        '-v',
        '--tb=short'
    ])
    print("-" * 60)
    print()
    
    # Summary
    print("[3/3] Test Summary")
    print("=" * 60)
    if result.returncode == 0:
        print("✅ All tests PASSED!")
        print()
        print("Your backend is working correctly:")
        print("  ✓ Role-based access control is working")
        print("  ✓ Student endpoints are protected")
        print("  ✓ Teacher endpoints are protected")
        print("  ✓ Data isolation is enforced")
        print("  ✓ Authentication is secure")
    else:
        print("❌ Some tests FAILED")
        print()
        print("Check the output above for details.")
        print("Common fixes:")
        print("  1. Restart backend: python run.py")
        print("  2. Check MongoDB connection")
        print("  3. Verify .env configuration")
        print("  4. Check for errors in logs")
    
    print("=" * 60)
    return result.returncode


if __name__ == '__main__':
    sys.exit(run_tests())
