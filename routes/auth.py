# routes/auth.py

from flask import Blueprint, request, jsonify
from lib.mongodb import get_database
from lib.auth import verify_password, generate_token, hash_password
from datetime import datetime
import traceback  # For detailed error logging

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be valid JSON'}), 400

        username = data.get('username')
        password = data.get('password')
        role = data.get('role')
        
        if not username or not password or not role:
            return jsonify({'error': 'Missing username, password, or role'}), 400
        
        try:
            db = get_database()
        except Exception as db_error:
            error_msg = str(db_error).replace('\n', ' ')
            return jsonify({
                'error': error_msg or 'Failed to connect to database. Please check your MongoDB connection string.'
            }), 503
        
        users_collection = db['users']
        user = users_collection.find_one({'username': username, 'role': role})
        
        if not user or not verify_password(password, user.get('password', '')):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user_data = {
            'id': str(user['_id']),
            'username': user['username'],
            'fullName': user['fullName'],
            'email': user['email'],
            'role': user['role']
        }
        
        token = generate_token(str(user['_id']), user['role'])
        return jsonify({'user': user_data, 'token': token}), 200
        
    except Exception as error:
        print("=== LOGIN ERROR ===")
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be valid JSON'}), 400

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('fullName')
        role = data.get('role', 'customer')
        
        # Validate all required fields
        if not all([username, email, password, full_name]):
            return jsonify({'error': 'Missing required fields: username, email, password, fullName'}), 400
        
        try:
            db = get_database()
        except Exception as db_error:
            error_msg = str(db_error).replace('\n', ' ')
            return jsonify({
                'error': error_msg or 'Failed to connect to database. Please check your MongoDB connection string.'
            }), 503
        
        users_collection = db['users']
        
        # Check for existing username or email
        if users_collection.find_one({'username': username}):
            return jsonify({'error': 'Username already exists'}), 400
        if users_collection.find_one({'email': email}):
            return jsonify({'error': 'Email already in use'}), 400
        
        # Hash password (will raise error if hash_password fails)
        hashed_password = hash_password(password)
        
        # Insert new user
        result = users_collection.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password,
            'fullName': full_name,
            'role': role,
            'createdAt': datetime.utcnow()
        })
        
        user = {
            'id': str(result.inserted_id),
            'username': username,
            'fullName': full_name,
            'email': email,
            'role': role
        }
        
        token = generate_token(str(result.inserted_id), role)
        return jsonify({'user': user, 'token': token}), 201
        
    except Exception as error:
        print("=== SIGNUP ERROR ===")
        traceback.print_exc()  # 👈 This shows the FULL error in terminal!
        # For development only — hide details in production
        return jsonify({'error': 'Internal server error', 'details': str(error)}), 500