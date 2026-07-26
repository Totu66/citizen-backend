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
        'role': data.get('role', 'citizen')
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
    if not user or not User.verify_password(user['password'], data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

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
