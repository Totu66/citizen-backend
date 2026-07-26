from flask import Blueprint, request, jsonify
from models.complaint import Complaint
from models.user import User
from functools import wraps

reports_bp = Blueprint('reports', __name__)

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
        if payload['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        request.user = payload
        return f(*args, **kwargs)
    return decorated

@reports_bp.route('/summary', methods=['GET'])
@token_required
def get_summary():
    category = request.args.get('category')

    stats = Complaint.get_stats()

    if category:
        pipeline = [
            {'$match': {'category': category}},
            {'$group': {
                '_id': '$status',
                'count': {'$sum': 1}
            }}
        ]
        results = list(Complaint.collection().aggregate(pipeline))
        filtered = {'total': 0, 'pending': 0, 'under_review': 0, 'in_progress': 0, 'resolved': 0}
        for r in results:
            filtered[r['_id']] = r['count']
            filtered['total'] += r['count']
        resolved = filtered['resolved']
        total = filtered['total']
    else:
        resolved = stats['resolved']
        total = stats['total']

    breakdown = Complaint.get_breakdown(category)

    return jsonify({
        'total': total,
        'resolved': resolved,
        'breakdown': breakdown
    })
