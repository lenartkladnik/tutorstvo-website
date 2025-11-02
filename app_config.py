from resources import secrets

SECRET_KEY = secrets['db']
AUTHORITY = f"https://login.microsoftonline.com/{secrets['tenant_id']}"
CLIENT_ID = secrets['client_id']
CLIENT_SECRET = secrets['client_secret']
REDIRECT_URI = secrets['redirect_uri']
SESSION_TYPE = "filesystem"

MAIL_ADDRESS = secrets['mail-address']
MAIL_SERVER = secrets['mail-server']
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = secrets['mail-username']
MAIL_PASSWORD = secrets['mail-password']

SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db?timeout=30'
SQLALCHEMY_BINDS = {
    'users': 'sqlite:///users.db?timeout=30',
    'subjects': 'sqlite:///subjects.db?timeout=30',
    'lessons': 'sqlite:///lessons.db?timeout=30',
    'groups': 'sqlite:///groups.db?timeout=30'
}

CACHE_TYPE = 'redis'
CACHE_REDIS_HOST = 'localhost'
CACHE_REDIS_PORT = 6379
