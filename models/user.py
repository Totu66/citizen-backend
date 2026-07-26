from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from config import SECRET_KEY, JWT_EXPIRATION_HOURS

class User:
    @staticmethod
    def collection():
        return current_app.mongo.db.users

    @staticmethod
    def create(data):
        data['password'] = generate_password_hash(data['password'])
        data['created_at'] = datetime.datetime.now(datetime.UTC)
        result = User.collection().insert_one(data)
        return User.collection().find_one({'_id': result.inserted_id})

    @staticmethod
    def find_by_email(email):
        return User.collection().find_one({'email': email})

    @staticmethod
    def find_by_id(user_id):
        from bson.objectid import ObjectId
        return User.collection().find_one({'_id': ObjectId(user_id)})

    @staticmethod
    def find_all(filters=None):
        q = filters or {}
        return list(User.collection().find(q).sort('created_at', -1))

    @staticmethod
    def delete_by_id(user_id):
        from bson.objectid import ObjectId
        return User.collection().delete_one({'_id': ObjectId(user_id)})

    @staticmethod
    def update_by_id(user_id, data):
        from bson.objectid import ObjectId
        User.collection().update_one({'_id': ObjectId(user_id)}, {'$set': data})
        return User.find_by_id(user_id)

    @staticmethod
    def verify_password(stored, provided):
        return check_password_hash(stored, provided)

    @staticmethod
    def generate_token(user_id, role):
        payload = {
            'user_id': str(user_id),
            'role': role,
            'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    @staticmethod
    def verify_token(token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return payload
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None
