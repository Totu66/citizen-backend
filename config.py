import os

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://winfredcherotich6_db_user:5qhncoO17XCuERDu@cluster0.i6j90nm.mongodb.net/')
MONGO_DB = os.environ.get('MONGO_DB', 'citizen_connect')
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-to-a-secure-secret-key-in-production')
JWT_EXPIRATION_HOURS = 24
