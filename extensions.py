from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import Flask
from flask_mail import Mail
from flask_caching import Cache
from resources import secrets

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
login_manager = LoginManager(app)
cache = Cache(app)
