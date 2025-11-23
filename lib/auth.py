# lib/auth.py
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import os
from datetime import datetime, timedelta
from lib.mongodb import get_database
from bson.objectid import ObjectId

SECRET_KEY = os.getenv('SECRET_KEY', 'JesmundIvanClariceGailMayeoh!')

def hash_password(password: str) -> str:
    """Hash a password using werkzeug"""
    return generate_password_hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return check_password_hash(hashed_password, password)

def generate_token(user_id: str, expires_in: int = 3600) -> str:
    """Generate a JWT token for a user"""
    payload = {
        'user_id': str(user_id),
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def verify_token(token: str) -> dict:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# <CHANGE> ADD THIS MISSING FUNCTION
def get_user_from_token(token: str) -> dict:
    """Get user information from a JWT token"""
    payload = verify_token(token)
    if not payload:
        return None
    
    try:
        db = get_database()
        user_id = payload.get('user_id')
        user = db.users.find_one({'_id': ObjectId(user_id)})
        return user
    except Exception as e:
        print(f"Error getting user from token: {e}")
        return None