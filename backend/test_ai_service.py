#!/usr/bin/env python
"""Test AI service configuration and connectivity"""
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

print("=== AI SERVICE DIAGNOSTICS ===\n")

# Check environment variables
print("1. Environment Variables:")
api_key = os.getenv('GOOGLE_API_KEY')
model = os.getenv('GOOGLE_MODEL', 'gemini-pro')
print(f"  GOOGLE_API_KEY: {'✓ Set' if api_key else '✗ NOT SET'} (first 20 chars: {api_key[:20] if api_key else 'N/A'}...)")
print(f"  GOOGLE_MODEL: {model}")

# Check package imports
print("\n2. Package Imports:")
try:
    import google.generativeai as genai
    print("  ✓ google-generativeai imported successfully")
except ImportError as e:
    print(f"  ✗ Failed to import google-generativeai: {e}")
    exit(1)

# Test API configuration
print("\n3. Google Generative AI Configuration:")
try:
    if api_key:
        genai.configure(api_key=api_key)
        print("  ✓ API configured with key")
    else:
        print("  ✗ No API key provided")
        exit(1)
except Exception as e:
    print(f"  ✗ Configuration error: {e}")
    exit(1)

# Test model availability
print("\n4. Model Availability:")
try:
    model_obj = genai.GenerativeModel(model)
    print(f"  ✓ Model '{model}' loaded successfully")
except Exception as e:
    print(f"  ✗ Model error: {e}")
    exit(1)

# Test simple generation
print("\n5. Test Simple Generation:")
try:
    response = model_obj.generate_content("Say 'Hello,  World!'")
    if response and response.text:
        print(f"  ✓ Generation successful")
        print(f"  Response: {response.text[:100]}...")
    else:
        print(f"  ✗ Empty response from model")
except Exception as e:
    print(f"  ✗ Generation error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== DIAGNOSTICS COMPLETE ===")
