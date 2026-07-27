import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, mongo
from werkzeug.security import generate_password_hash
import datetime

app = create_app()

with app.app_context():
    existing = mongo.db.users.find_one({'email': 'admin@londiani.go.ke'})
    if existing:
        print('Admin user already exists, skipping seed.')
    else:
        mongo.db.users.insert_one({
            'name': 'Admin Londiani',
            'email': 'admin@londiani.go.ke',
            'phone': '0700111222',
            'ward': 'Londiani',
            'password': generate_password_hash('admin123'),
            'role': 'admin',
            'login_attempts': 0,
            'locked': False,
            'created_at': datetime.datetime.utcnow()
        })
        print('Admin user created: admin@londiani.go.ke / admin123')

    existing_citizen = mongo.db.users.find_one({'email': 'citizen@test.com'})
    if not existing_citizen:
        mongo.db.users.insert_one({
            'name': 'Test Citizen',
            'email': 'citizen@test.com',
            'phone': '0700222333',
            'ward': 'Kedowa',
            'password': generate_password_hash('citizen123'),
            'role': 'citizen',
            'login_attempts': 0,
            'locked': False,
            'created_at': datetime.datetime.utcnow()
        })
        print('Test citizen created: citizen@test.com / citizen123')

    sample_count = mongo.db.complaints.count_documents({})
    if sample_count == 0:
        citizen = mongo.db.users.find_one({'email': 'citizen@test.com'})
        samples = [
            {'citizen_id': citizen['_id'], 'title': 'Pothole on Londiani-Kedowa road', 'description': 'Large pothole near the junction causing traffic delays and vehicle damage.', 'category': 'roads', 'location': 'Londiani-Kedowa road junction', 'priority': 'high', 'status': 'in_progress', 'created_at': datetime.datetime.utcnow() - datetime.timedelta(days=5), 'updated_at': datetime.datetime.utcnow() - datetime.timedelta(days=2)},
            {'citizen_id': citizen['_id'], 'title': 'Water shortage in Kunyak area', 'description': 'No running water for the past week in Kunyak village.', 'category': 'water', 'location': 'Kunyaka village', 'priority': 'high', 'status': 'pending', 'created_at': datetime.datetime.utcnow() - datetime.timedelta(days=3), 'updated_at': datetime.datetime.utcnow() - datetime.timedelta(days=3)},
            {'citizen_id': citizen['_id'], 'title': 'Broken street lights in Londiani town', 'description': 'Street lights along the main street have been broken for a month.', 'category': 'electricity', 'location': 'Londiani town main street', 'priority': 'medium', 'status': 'resolved', 'created_at': datetime.datetime.utcnow() - datetime.timedelta(days=20), 'updated_at': datetime.datetime.utcnow() - datetime.timedelta(days=5)},
            {'citizen_id': citizen['_id'], 'title': 'Garbage not collected', 'description': 'Garbage has not been collected in our estate for two weeks.', 'category': 'sanitation', 'location': 'Londiani estate block B', 'priority': 'medium', 'status': 'under_review', 'created_at': datetime.datetime.utcnow() - datetime.timedelta(days=7), 'updated_at': datetime.datetime.utcnow() - datetime.timedelta(days=6)},
            {'citizen_id': citizen['_id'], 'title': 'Suspicious activity at night', 'description': 'Unknown individuals loitering around the market area after dark.', 'category': 'security', 'location': 'Londiani market area', 'priority': 'high', 'status': 'pending', 'created_at': datetime.datetime.utcnow() - datetime.timedelta(days=1), 'updated_at': datetime.datetime.utcnow() - datetime.timedelta(days=1)},
        ]
        mongo.db.complaints.insert_many(samples)
        print(f'Created {len(samples)} sample complaints.')

    print('Database seeded successfully!')
