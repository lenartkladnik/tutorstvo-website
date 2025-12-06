from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_mail import Mail
from flask_caching import Cache
from identity.flask import Auth
from flask_migrate import Migrate
import app_config
from resources import log
from apscheduler.schedulers.background import BackgroundScheduler

log("Setting up configuration.", "extensions")

app = Flask(__name__)
scheduler = BackgroundScheduler()

app.config.from_object(app_config)
app.jinja_env.add_extension('jinja2.ext.do')

mail = Mail(app)
db = SQLAlchemy(app)
cache = Cache(app)

from models import User, Subject, Lesson, Group, LessonRequest, Stats # Needed because of db creation ->
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

migrate = Migrate(app, db)

BASE_SUBJECTS = ["Matematika", "Slovenščina", "Zgodovina", "Psihologija", "Angleščina", "Sociologija", "Španščina", "Nemščina", "Francoščina", "Kemija", "Fizika", "Biologija", "Geografija", "Glasba", "Likovna", "Drugo"]

with app.app_context():
    if Subject.query.count() == 0:
        for subject in BASE_SUBJECTS:
            db.session.add(Subject(name=subject, tutors=''))

        db.session.commit()

log("Configuration is set up.", "extensions")
