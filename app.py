from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_pymongo import PyMongo
from config import MONGO_URI, MONGO_DB, SECRET_KEY

mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config['MONGO_URI'] = MONGO_URI + MONGO_DB
    app.config['SECRET_KEY'] = SECRET_KEY
    CORS(app)

    mongo.init_app(app)
    app.mongo = mongo

    from routes.auth import auth_bp
    from routes.complaints import complaints_bp
    from routes.reports import reports_bp
    from routes.users import users_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(complaints_bp, url_prefix='/api/complaints')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(users_bp, url_prefix='/api/users')

    @app.route('/api/health')
    def health():
        return {'status': 'ok'}

    @app.route('/api/complaints/public')
    def public_complaints():
        from models.complaint import Complaint
        from models.user import User
        limit = int(request.args.get('limit', 20))
        complaints = Complaint.find_all({}, limit)
        result = []
        for c in complaints:
            citizen = User.find_by_id(c['citizen_id'])
            result.append({
                '_id': str(c['_id']),
                'citizen_name': citizen['name'] if citizen else 'Unknown',
                'title': c['title'],
                'description': c['description'],
                'category': c['category'],
                'location': c['location'],
                'priority': c['priority'],
                'status': c['status'],
                'created_at': c['created_at'].isoformat() if c.get('created_at') else None
            })
        return jsonify({'complaints': result})

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
