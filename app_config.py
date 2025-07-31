from resources import secrets

SECRET_KEY = secrets['db']
AUTHORITY = f"https://login.microsoftonline.com/{secrets['tenant_id']}"
CLIENT_ID = secrets['client_id']
CLIENT_SECRET = secrets['client_secret']
REDIRECT_URI = "http://localhost:5000/getAToken"
SESSION_TYPE = "filesystem"

MAIL_ADDRESS = 'tutorstvo@kladnik.cc'
MAIL_SERVER = 'smtp-relay.brevo.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = secrets['mail-username']
MAIL_PASSWORD = secrets['mail-password']

SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
SQLALCHEMY_BINDS = {
    'users': 'sqlite:///users.db',
    'subjects': 'sqlite:///subjects.db',
    'lessons': 'sqlite:///lessons.db',
    'groups': 'sqlite:///groups.db'
}

CACHE_TYPE = 'redis'
CACHE_REDIS_HOST = 'localhost'
CACHE_REDIS_PORT = 6379
