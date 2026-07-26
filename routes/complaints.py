from flask import Blueprint, request, jsonify
from models.complaint import Complaint
from models.response import Response
from models.user import User
from bson.objectid import ObjectId
from functools import wraps

complaints_bp = Blueprint('complaints', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        token = auth.split(' ')[1]
        payload = User.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        request.user = payload
        return f(*args, **kwargs)
    return decorated

@complaints_bp.route('', methods=['POST'])
@token_required
def create_complaint():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required = ['title', 'description', 'category', 'location']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    complaint_data = {
        'citizen_id': ObjectId(request.user['user_id']),
        'title': data['title'],
        'description': data['description'],
        'category': data['category'],
        'location': data['location'],
        'priority': data.get('priority', 'medium')
    }

    complaint = Complaint.create(complaint_data)
    complaint['_id'] = str(complaint['_id'])
    complaint['citizen_id'] = str(complaint['citizen_id'])

    return jsonify({'complaint': complaint}), 201

@complaints_bp.route('', methods=['GET'])
@token_required
def get_complaints():
    filters = {}
    if request.args.get('status'):
        filters['status'] = request.args['status']
    if request.args.get('category'):
        filters['category'] = request.args['category']
    if request.args.get('priority'):
        filters['priority'] = request.args['priority']

    limit = int(request.args.get('limit', 50))
    complaints = Complaint.find_all(filters, limit)

    result = []
    for c in complaints:
        citizen = User.find_by_id(c['citizen_id'])
        result.append({
            '_id': str(c['_id']),
            'citizen_id': str(c['citizen_id']),
            'citizen_name': citizen['name'] if citizen else 'Unknown',
            'title': c['title'],
            'description': c['description'],
            'category': c['category'],
            'location': c['location'],
            'priority': c['priority'],
            'status': c['status'],
            'created_at': c['created_at'].isoformat() if c.get('created_at') else None,
            'updated_at': c['updated_at'].isoformat() if c.get('updated_at') else None
        })

    return jsonify({'complaints': result})

@complaints_bp.route('/mine', methods=['GET'])
@token_required
def get_my_complaints():
    complaints = Complaint.find_by_citizen(request.user['user_id'])
    result = []
    for c in complaints:
        result.append({
            '_id': str(c['_id']),
            'title': c['title'],
            'description': c['description'],
            'category': c['category'],
            'location': c['location'],
            'priority': c['priority'],
            'status': c['status'],
            'created_at': c['created_at'].isoformat() if c.get('created_at') else None,
            'updated_at': c['updated_at'].isoformat() if c.get('updated_at') else None
        })
    return jsonify({'complaints': result})

@complaints_bp.route('/<complaint_id>', methods=['GET'])
@token_required
def get_complaint(complaint_id):
    complaint = Complaint.find_by_id(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    citizen = User.find_by_id(complaint['citizen_id'])
    responses = Response.find_by_complaint(complaint_id)

    result = {
        '_id': str(complaint['_id']),
        'citizen_id': str(complaint['citizen_id']),
        'citizen_name': citizen['name'] if citizen else 'Unknown',
        'title': complaint['title'],
        'description': complaint['description'],
        'category': complaint['category'],
        'location': complaint['location'],
        'priority': complaint['priority'],
        'status': complaint['status'],
        'created_at': complaint['created_at'].isoformat() if complaint.get('created_at') else None,
        'updated_at': complaint['updated_at'].isoformat() if complaint.get('updated_at') else None
    }

    resp_list = []
    for r in responses:
        resp_list.append({
            '_id': str(r['_id']),
            'action_taken': r.get('action_taken', ''),
            'department': r.get('department', ''),
            'remarks': r.get('remarks', ''),
            'responded_at': r['responded_at'].isoformat() if r.get('responded_at') else None
        })

    return jsonify({'complaint': result, 'responses': resp_list})

@complaints_bp.route('/<complaint_id>/status', methods=['PUT'])
@token_required
def update_complaint_status(complaint_id):
    if request.user['role'] != 'admin':
        return jsonify({'error': 'Only admins can update complaint status'}), 403

    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400

    valid_statuses = ['pending', 'under_review', 'in_progress', 'resolved']
    if data['status'] not in valid_statuses:
        return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400

    update_data = {'status': data['status']}
    complaint = Complaint.update_status(complaint_id, update_data)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    if data.get('action_taken'):
        response_data = {
            'complaint_id': ObjectId(complaint_id),
            'admin_id': ObjectId(request.user['user_id']),
            'action_taken': data['action_taken'],
            'department': data.get('department', ''),
            'remarks': data.get('remarks', '')
        }
        Response.create(response_data)

    complaint['_id'] = str(complaint['_id'])
    if 'citizen_id' in complaint:
        complaint['citizen_id'] = str(complaint['citizen_id'])
    return jsonify({'complaint': complaint})

@complaints_bp.route('/stats', methods=['GET'])
@token_required
def get_stats():
    stats = Complaint.get_stats()
    return jsonify({'stats': stats})
