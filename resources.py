import itsdangerous

DATETIME_FORMAT_JS = "%Y/%d/%m"
DATETIME_FORMAT_PY = '%d-%m-%Y'

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
    raise RuntimeError(f"Secret key file '{_secrets_fp}' not found.")

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
