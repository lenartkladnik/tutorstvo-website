import itsdangerous
from datetime import datetime
import os
from functools import wraps
from flask import abort

DATETIME_FORMAT_JS = "%Y/%d/%m"
DATETIME_FORMAT_PY = '%d-%m-%Y'
log_dir = 'logs'
if not os.path.isdir(log_dir):
    os.mkdir(log_dir)
LOG_PATH = os.path.join(log_dir, f'tutorstvo-{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.log')

secrets: dict = {}
_secrets_fp = '.secrets'

try:
    with open(_secrets_fp) as f:
        f.seek(0)
        for i in f.readlines():
            ln = i.strip().split(':', 1)
            
            if len(ln) > 1:
                secrets.update({ln[0]: ln[1]})

except FileNotFoundError:
    raise RuntimeError(f"Settings file '{_secrets_fp}' not found.")

DEBUG = secrets['DEBUG']
if DEBUG.isdigit():
    DEBUG = int(DEBUG)

else:
    raise RuntimeError(f"DEBUG must be an int.")

serializer = itsdangerous.URLSafeTimedSerializer(secrets['db'])

def formatTitle(title: str) -> str:
    split_tile = list(map(str.strip, title.split(',')))

    f = []
    for i in split_tile:
        f.append(' '.join(list(map(lambda x: x.lower().capitalize(), i.split(' ')))))

    return ', '.join(f)

def generate_confirmation_token(email):
    token = serializer.dumps(email, salt=f"confirm-email")
    return token

def confirm_token(token):
    try:
        email = serializer.loads(
                token,
                salt=f"confirm-email",
                max_age=3600
            )
        
        return email
    except itsdangerous.SignatureExpired:
        return False 
    except itsdangerous.BadSignature:
        return False

def log(message: str, log_path: str, log_type: str = 'info'):
    current_time = datetime.now().strftime("%H:%M:%S")

    log_string = f"[{current_time}] {log_type.upper()} \"{log_path}\": {message}"

    if log_type == 'warn' or log_type == 'warning':
        print('\x1b[38;5;202m', end='')

    elif log_type == 'err' or log_type == 'error':
        print('\x1b[38;5;160m', end='')

    print(log_string, '\x1b[0m', sep='')

    with open(LOG_PATH, 'a') as f:
        f.write(log_string + '\n')

def debug_only(func):
    """
    Run the function only if the app is running in debug mode.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if DEBUG > 0:
            return func(*args, **kwargs)

        return abort(404)

    return wrapper
