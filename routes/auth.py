from flask import Blueprint, request, jsonify
from models.user import User
from bson.objectid import ObjectId

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required = ['name', 'email', 'phone', 'password', 'ward']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    if User.find_by_email(data['email']):
        return jsonify({'error': 'Email already registered'}), 400

    user_data = {
        'name': data['name'],
        'email': data['email'],
        'phone': data['phone'],
        'ward': data.get('ward', ''),
        'password': data['password'],
        'role': 'citizen'
    }

    user = User.create(user_data)
    token = User.generate_token(user['_id'], user['role'])

    return jsonify({
        'token': token,
        'user': {
            '_id': str(user['_id']),
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'ward': user['ward']
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.find_by_email(data['email'])

    if user and user.get('locked'):
        return jsonify({'error': 'Account is blocked due to too many failed login attempts.'}), 403

    if not user or not User.verify_password(user['password'], data['password']):
        if user:
            attempts = user.get('login_attempts', 0) + 1
            if attempts >= 3:
                User.collection().update_one({'_id': user['_id']}, {'$set': {'login_attempts': attempts, 'locked': True}})
                return jsonify({'error': 'Wrong password. Account has been blocked due to too many failed attempts.'}), 403
            else:
                User.collection().update_one({'_id': user['_id']}, {'$set': {'login_attempts': attempts}})
                remaining = 3 - attempts
                return jsonify({'error': f'Wrong password. {remaining} attempt(s) remaining.'}), 401
        return jsonify({'error': 'Wrong password.'}), 401

    User.collection().update_one({'_id': user['_id']}, {'$set': {'login_attempts': 0}})

    token = User.generate_token(user['_id'], user['role'])

    return jsonify({
        'token': token,
        'user': {
            '_id': str(user['_id']),
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'ward': user['ward']
        }
    })
