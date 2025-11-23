from pymongo import MongoClient
from flask import Flask
import os

db = None

def init_db(app: Flask):
    """Initialize MongoDB connection"""
    global db
    
    try:
        uri = os.getenv('MONGODB_URI')
        db_name = os.getenv('MONGODB_DB_NAME', 'ayudabesh')
        
        if not uri:
            raise ValueError("MONGODB_URI is not set in environment variables")
        
        client = MongoClient(uri)
        db = client[db_name]
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB")
        
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        raise


def get_database():
    """Returns the MongoDB database instance"""
    if db is None:
        raise RuntimeError("Database not initialized. Call init_db(app) first in your app startup.")
    return db