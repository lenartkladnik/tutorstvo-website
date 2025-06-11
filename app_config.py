from resources import secrets

SECRET_KEY = secrets['db']
AUTHORITY = f"https://login.microsoftonline.com/{secrets['tenant_id']}"
CLIENT_ID = secrets['client_id']
CLIENT_SECRET = secrets['client_secret']
REDIRECT_URI = "http://localhost:5000/getAToken"
SESSION_TYPE = "filesystem" # NOT FOR PROD
