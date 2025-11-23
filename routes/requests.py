from flask import Blueprint, request, jsonify
from lib.mongodb import get_database
from lib.auth import get_user_from_token
from bson import ObjectId
from datetime import datetime

requests_bp = Blueprint('requests', __name__)

def get_current_user():
    """Extract current user from request headers"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        # Fallback to x-user header for compatibility
        user_str = request.headers.get('x-user')
        if user_str:
            try:
                import json
                return json.loads(user_str)
            except:
                return None
        return None
    
    # Extract token from "Bearer <token>" format
    try:
        token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        user_info = get_user_from_token(token)
        if user_info:
            # Get full user data from database
            try:
                db = get_database()
                users_collection = db['users']
                user = users_collection.find_one({'_id': ObjectId(user_info['id'])})
                if user:
                    return {
                        'id': str(user['_id']),
                        'username': user['username'],
                        'fullName': user['fullName'],
                        'email': user['email'],
                        'role': user['role']
                    }
            except Exception as db_error:
                print(f"Database error in get_current_user: {db_error}")
                return None
    except Exception as e:
        print(f"Error extracting user from token: {e}")
    
    return None

@requests_bp.route('/create', methods=['POST'])
def create_request():
    """Create a new service request"""
    try:
        data = request.get_json()
        service_id = data.get('serviceId')
        status = data.get('status', 'pending')
        
        user = get_current_user()
        
        if not user or not service_id:
            return jsonify({'error': 'Missing required fields'}), 400
        
        try:
            db = get_database()
        except Exception as db_error:
            error_msg = str(db_error).replace('\n', ' ')
            return jsonify({
                'error': error_msg or 'Failed to connect to database. Please check your MongoDB connection string.'
            }), 503
        
        requests_collection = db['service_requests']
        
        result = requests_collection.insert_one({
            'customerId': user['id'],
            'customerName': user['fullName'],
            'serviceId': service_id,
            'serviceName': 'Service',  # This would normally come from a services collection
            'status': status,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        })
        
        return jsonify({
            'id': str(result.inserted_id),
            'message': 'Request created'
        }), 201
        
    except Exception as error:
        print(f"Create request error: {error}")
        return jsonify({'error': 'Internal server error'}), 500

@requests_bp.route('/my-requests', methods=['GET'])
def get_my_requests():
    """Get all requests for the current user"""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        try:
            db = get_database()
        except Exception as db_error:
            error_msg = str(db_error).replace('\n', ' ')
            return jsonify({
                'error': error_msg or 'Failed to connect to database. Please check your MongoDB connection string.'
            }), 503
        
        requests_collection = db['service_requests']
        
        requests = list(requests_collection.find(
            {'customerId': user['id']}
        ).sort('createdAt', -1))
        
        # Convert ObjectId to string for JSON serialization
        for req in requests:
            req['_id'] = str(req['_id'])
            if 'createdAt' in req:
                req['createdAt'] = req['createdAt'].isoformat() if hasattr(req['createdAt'], 'isoformat') else str(req['createdAt'])
            if 'updatedAt' in req:
                req['updatedAt'] = req['updatedAt'].isoformat() if hasattr(req['updatedAt'], 'isoformat') else str(req['updatedAt'])
        
        return jsonify(requests), 200
        
    except Exception as error:
        print(f"Fetch requests error: {error}")
        return jsonify({'error': 'Internal server error'}), 500

@requests_bp.route('/pending', methods=['GET'])
def get_pending_requests():
    """Get all pending service requests"""
    try:
        try:
            db = get_database()
        except Exception as db_error:
            error_msg = str(db_error).replace('\n', ' ')
            return jsonify({
                'error': error_msg or 'Failed to connect to database. Please check your MongoDB connection string.'
            }), 503
        
        requests_collection = db['service_requests']
        
        requests = list(requests_collection.find(
            {'status': 'pending'}
        ).sort('createdAt', -1))
        
        # Convert ObjectId to string for JSON serialization
        for req in requests:
            req['_id'] = str(req['_id'])
            if 'createdAt' in req:
                req['createdAt'] = req['createdAt'].isoformat() if hasattr(req['createdAt'], 'isoformat') else str(req['createdAt'])
            if 'updatedAt' in req:
                req['updatedAt'] = req['updatedAt'].isoformat() if hasattr(req['updatedAt'], 'isoformat') else str(req['updatedAt'])
        
        return jsonify(requests), 200
        
    except Exception as error:
        print(f"Fetch pending requests error: {error}")
        return jsonify({'error': 'Internal server error'}), 500

@requests_bp.route('/<request_id>', methods=['PATCH'])
def update_request(request_id):
    """Update a service request status"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        if not status:
            return jsonify({'error': 'Missing status field'}), 400
        
        try:
            db = get_database()
        except Exception as db_error:
            error_msg = str(db_error).replace('\n', ' ')
            return jsonify({
                'error': error_msg or 'Failed to connect to database. Please check your MongoDB connection string.'
            }), 503
        
        requests_collection = db['service_requests']
        
        try:
            result = requests_collection.update_one(
                {'_id': ObjectId(request_id)},
                {
                    '$set': {
                        'status': status,
                        'updatedAt': datetime.utcnow()
                    }
                }
            )
        except Exception as e:
            return jsonify({'error': 'Invalid request ID'}), 400
        
        if result.matched_count == 0:
            return jsonify({'error': 'Request not found'}), 404
        
        return jsonify({'message': 'Request updated'}), 200
        
    except Exception as error:
        print(f"Update request error: {error}")
        return jsonify({'error': 'Internal server error'}), 500

