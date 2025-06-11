from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_mail import Mail
from flask_caching import Cache
from resources import secrets
from identity.flask import Auth
import app_config

app = Flask(__name__)

app.config['MAIL_SERVER']= 'smtp-relay.brevo.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = secrets['mail-username']
app.config['MAIL_PASSWORD'] = secrets['mail-password']

mail = Mail(app)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.db'
app.config["SQLALCHEMY_BINDS"] = {
    'users': 'sqlite:///users.db',
    'subjects': 'sqlite:///subjects.db',
    'lessons': 'sqlite:///lessons.db',
    'groups': 'sqlite:///groups.db'
}

app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_HOST'] = 'localhost'
app.config['CACHE_REDIS_PORT'] = 6379

db = SQLAlchemy(app)
cache = Cache(app)

from models import User, Subject, Lesson, Group # Needed because of db creation ->
                                                # SQLAlchemy won't create the db
                                                # tables if they aren't imported

with app.app_context():
    db.create_all()

app.config.from_object(app_config)

auth = Auth(
    app,
    authority=app.config["AUTHORITY"],
    client_id=app.config["CLIENT_ID"],
    client_credential=app.config["CLIENT_SECRET"],
    redirect_uri=app.config["REDIRECT_URI"]
)
