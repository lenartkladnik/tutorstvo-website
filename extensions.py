from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_mail import Mail
from flask_caching import Cache
from identity.flask import Auth
import app_config
from resources import log

log("Setting up configuration.", "extensions")

app = Flask(__name__)

app.config.from_object(app_config)

mail = Mail(app)
db = SQLAlchemy(app)
cache = Cache(app)

from models import User, Subject, Lesson, Group # Needed because of db creation ->
                                                # SQLAlchemy won't create the db
                                                # tables if they aren't imported

with app.app_context():
    db.create_all()

auth = Auth(
    app,
    authority=app.config["AUTHORITY"],
    client_id=app.config["CLIENT_ID"],
    client_credential=app.config["CLIENT_SECRET"],
    redirect_uri=app.config["REDIRECT_URI"]
)

log("Configuration is set up.", "extensions")
