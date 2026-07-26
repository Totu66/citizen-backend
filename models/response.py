import datetime
from flask import current_app
from bson.objectid import ObjectId

class Response:
    @staticmethod
    def collection():
        return current_app.mongo.db.responses

    @staticmethod
    def create(data):
        data['responded_at'] = datetime.datetime.now(datetime.UTC)
        result = Response.collection().insert_one(data)
        return Response.collection().find_one({'_id': result.inserted_id})

    @staticmethod
    def find_by_complaint(complaint_id):
        return list(Response.collection().find(
            {'complaint_id': ObjectId(complaint_id)}
        ).sort('responded_at', -1))
