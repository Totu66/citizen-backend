import datetime
from flask import current_app
from bson.objectid import ObjectId

class Complaint:
    @staticmethod
    def collection():
        return current_app.mongo.db.complaints

    @staticmethod
    def create(data):
        data['status'] = 'pending'
        data['created_at'] = datetime.datetime.now(datetime.UTC)
        data['updated_at'] = data['created_at']
        result = Complaint.collection().insert_one(data)
        return Complaint.collection().find_one({'_id': result.inserted_id})

    @staticmethod
    def find_by_id(complaint_id):
        return Complaint.collection().find_one({'_id': ObjectId(complaint_id)})

    @staticmethod
    def find_by_citizen(citizen_id):
        return list(Complaint.collection().find(
            {'citizen_id': ObjectId(citizen_id)}
        ).sort('created_at', -1))

    @staticmethod
    def find_all(filters=None, limit=50):
        query = filters or {}
        return list(Complaint.collection().find(query).sort('created_at', -1).limit(limit))

    @staticmethod
    def update_status(complaint_id, status_data):
        status_data['updated_at'] = datetime.datetime.now(datetime.UTC)
        Complaint.collection().update_one(
            {'_id': ObjectId(complaint_id)},
            {'$set': status_data}
        )
        return Complaint.collection().find_one({'_id': ObjectId(complaint_id)})

    @staticmethod
    def get_stats():
        pipeline = [
            {'$group': {
                '_id': '$status',
                'count': {'$sum': 1}
            }}
        ]
        results = list(Complaint.collection().aggregate(pipeline))
        stats = {'total': 0, 'pending': 0, 'under_review': 0, 'in_progress': 0, 'resolved': 0}
        for r in results:
            stats[r['_id']] = r['count']
            stats['total'] += r['count']
        return stats

    @staticmethod
    def get_breakdown(category=None):
        match = {}
        if category:
            match['category'] = category
        pipeline = [
            {'$match': match},
            {'$group': {
                '_id': '$category',
                'total': {'$sum': 1},
                'pending': {'$sum': {'$cond': [{'$eq': ['$status', 'pending']}, 1, 0]}},
                'under_review': {'$sum': {'$cond': [{'$eq': ['$status', 'under_review']}, 1, 0]}},
                'in_progress': {'$sum': {'$cond': [{'$eq': ['$status', 'in_progress']}, 1, 0]}},
                'resolved': {'$sum': {'$cond': [{'$eq': ['$status', 'resolved']}, 1, 0]}}
            }}
        ]
        return list(Complaint.collection().aggregate(pipeline))
