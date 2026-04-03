#!/usr/bin/env python
"""Check MongoDB database contents"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
db_name = os.getenv('MONGODB_DB_NAME', 'educational_platform')

print(f"Connecting to: {mongodb_uri}")
print(f"Database: {db_name}")

try:
    client = MongoClient(mongodb_uri)
    db = client[db_name]
    
    # Check connection
    db.command('ping')
    print("✓ MongoDB connection successful")
    
    # List all databases
    print("\nAvailable databases:")
    for database in client.list_database_names():
        print(f"  - {database}")
    
    # Check users collection
    users_count = db['users'].count_documents({})
    print(f"\n✓ Users collection: {users_count} documents")
    
    if users_count > 0:
        print("\nUsers in database:")
        for user in db['users'].find().limit(10):
            print(f"  _id: {user.get('_id')}")
            print(f"  email: {user.get('email')}")
            print(f"  name: {user.get('name')}")
            print(f"  role: {user.get('role')}")
            print()
    
    # Check other collections
    for collection_name in ['chats', 'notes', 'assessments', 'progress']:
        count = db[collection_name].count_documents({})
        print(f"✓ {collection_name} collection: {count} documents")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
