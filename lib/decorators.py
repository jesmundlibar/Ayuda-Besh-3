# lib/decorators.py

from functools import wraps
from flask import request, jsonify, redirect, url_for
from lib.auth import verify_token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check header first
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
                print(f"🔒 TOKEN FROM HEADER: {token[:10]}...")

        # Check cookie if header missing
        if not token:
            token = request.cookies.get('token')
            if token:
                print(f"🔒 TOKEN FROM COOKIE: {token[:10]}...")
            else:
                print("🔒 NO TOKEN IN HEADER OR COOKIE")

        if not token:
            if not request.path.startswith('/api/'):
                print(f"🔒 REDIRECT TO LOGIN (no token) - Path: {request.path}")
                return redirect(url_for('frontend.login'))
            return jsonify({'error': 'Token missing'}), 401

        payload = verify_token(token)
        if not payload:
            if not request.path.startswith('/api/'):
                print(f"🔒 REDIRECT TO LOGIN (invalid token) - Path: {request.path}")
                return redirect(url_for('frontend.login'))
            return jsonify({'error': 'Invalid token'}), 401

        request.current_user = payload
        return f(*args, **kwargs)

    return decorated