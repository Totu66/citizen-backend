from flask import Blueprint, request, jsonify
from models.user import User
from functools import wraps

users_bp = Blueprint('users', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        token = auth.split(' ')[1]
        payload = User.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        if payload['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        request.user = payload
        return f(*args, **kwargs)
    return decorated

@users_bp.route('', methods=['GET'])
@admin_required
def list_users():
    users = User.find_all()
    result = []
    for u in users:
        result.append({
            '_id': str(u['_id']),
            'name': u['name'],
            'email': u['email'],
            'phone': u.get('phone', ''),
            'ward': u.get('ward', ''),
            'role': u['role'],
            'created_at': u['created_at'].isoformat() if u.get('created_at') else None
        })
    return jsonify({'users': result})

@users_bp.route('', methods=['POST'])
@admin_required
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    required = ['name', 'email', 'password']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    if User.find_by_email(data['email']):
        return jsonify({'error': 'Email already exists'}), 400
    role = data.get('role', 'citizen')
    if role not in ('admin', 'citizen'):
        return jsonify({'error': 'Role must be admin or citizen'}), 400
    user_data = {
        'name': data['name'],
        'email': data['email'],
        'phone': data.get('phone', ''),
        'ward': data.get('ward', ''),
        'password': data['password'],
        'role': role
    }
    user = User.create(user_data)
    return jsonify({
        '_id': str(user['_id']),
        'name': user['name'],
        'email': user['email'],
        'role': user['role']
    }), 201

@users_bp.route('/<user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    update = {}
    for field in ('name', 'email', 'phone', 'ward', 'role'):
        if field in data:
            update[field] = data[field]
    if 'password' in data and data['password']:
        from werkzeug.security import generate_password_hash
        update['password'] = generate_password_hash(data['password'])
    if update:
        User.update_by_id(user_id, update)
    updated = User.find_by_id(user_id)
    return jsonify({
        '_id': str(updated['_id']),
        'name': updated['name'],
        'email': updated['email'],
        'phone': updated.get('phone', ''),
        'ward': updated.get('ward', ''),
        'role': updated['role']
    })

@users_bp.route('/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if str(user['_id']) == request.user['user_id']:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    User.delete_by_id(user_id)
    return jsonify({'message': 'User deleted'})
