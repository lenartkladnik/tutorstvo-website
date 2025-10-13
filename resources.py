from typing import Callable, Any
import itsdangerous
from datetime import datetime
import os
from functools import wraps
from flask import abort, url_for
import math
from urllib.parse import urlparse

DATETIME_FORMAT_JS = "%Y/%d/%m"
DATETIME_FORMAT_PY = '%d-%m-%Y'
DATETIME_FORMAT_USER = '%d/%m/%Y'

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

FORM_VALIDATION_OFF = secrets['FORM_VALIDATION_OFF'] == '1'

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

def validate_form(form: Any, *checks: tuple[str, Callable], getter: str | None = None) -> bool:
    if FORM_VALIDATION_OFF:
        return True

    for name, func in checks:
        args = "undefined"
        try:
            args = form[name] if getter == "[]" or not getter else form.get(name) if getter == "get" else form.getlist(name) if getter == "getlist" else None
            if not func(args):
                log(f"Form validation failed on function: '{func.__name__}' with args: '{args}' ({name}).", "resources.validate_form")
                return False
        except KeyError:
            log(f"Form validation failed on function: '{func.__name__}' because of missing args.", "resources.validate_form")
            return False

        except Exception as e:
            log(f"Form validation failed on function: '{func.__name__}' with args: '{args}' ({name}) and exception: '{e}'.", "resources.validate_form")
            return False

    return True

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

def get_leaderboard(User, Subject):
    sorted_tutors = []
    for s in Subject.query.all():
        for t in s.get_tutors():
            sorted_tutors.append(t)

    sorted_tutors = list(set(sorted_tutors))

    sorted_tutors = sorted(sorted_tutors, key=lambda t: User.query.filter_by(username=t).first().score)[::-1]

    if len(sorted_tutors) == 0:
        return []

    max_score = User.query.filter_by(username=sorted_tutors[0]).first().score
    lb = zip(sorted_tutors,
             [i + 1 for i in range(len(sorted_tutors))],
             [User.query.filter_by(username=t).first().score / max_score * 100 if max_score > 0 else 100 for t in sorted_tutors],
             [User.query.filter_by(username=t).first().score for t in sorted_tutors]
             )

    return lb

def get_free_for_date(date: datetime, schedule: list, hour):
    all_classrooms = ["knj", "msv", "mpk", "mdž"]# ["m3", "r3", "r4", "vp", "mp", "s3", "k2", "r2", "f1", "mf", "k1", "n2", "b1", "b2", "m1", "m2", "r1", "ge", "zg", "a1", "a2", "n1", "s1", "rač", "knj", "msv", "mpk", "mdž"]
    always_free = ["knj", "msv", "mpk", "mdž"]

    if hour == "PRE" or hour == "O":
        return all_classrooms

    hour = int(hour)

    slovenian_days = [
        "Nedelja",
        "Ponedeljek", 
        "Torek",
        "Sreda",
        "Četrtek",
        "Petek",
        "Sobota"
    ]

    school_year_start = datetime(date.year, 9, 1)
    if date < school_year_start:
        school_year_start = datetime(school_year_start.year - 1, 9, 1)

    ms_per_week = 7 * 24 * 60 * 60 * 1000
    week_diff = math.floor((date - school_year_start).total_seconds() * 1000 / ms_per_week)

    week_type = "A" if week_diff % 2 == 0 else "B"
    day_name = slovenian_days[date.weekday() + 1 if date.weekday() < 6 else 0]

    indices = []
    for i, entry in enumerate(schedule):
        if entry[0] == week_type and entry[1] == day_name:
            indices.append(i)

    if hour >= len(indices):
        return all_classrooms

    free = schedule[indices[hour]].copy()
    if not free:
        return all_classrooms

    free.append(always_free)
    free[3] = [*free[3], *free[4]]
    free.pop()

    return free[3]

def parse_hour(time_str):
    periods = [
        {'label': 'PRE', 'start': '7:10', 'end': '7:55'},
        {'label': 'O',   'start': '10:25', 'end': '10:55'},
        {'label': '6',   'start': '12:40', 'end': '13:25'},
        {'label': '7',   'start': '13:30', 'end': '14:15'},
        {'label': '8',   'start': '14:20', 'end': '15:05'},
    ]

    for period in periods:
        if time_str.strip() == period['start'].strip():
            return period['label']

    return None

def safe_redirect(target: str):
    if not target:
        return url_for('views.home')

    ref_url = urlparse(target)

    return target if ref_url.netloc in secrets['hosts'].split(',') else url_for('views.home')

def is_lesson_removable(lesson):
    lesson_datetime = datetime.strptime(lesson.datetime.split(' ')[0], DATETIME_FORMAT_JS)
    lesson_datetime_20h = lesson_datetime.replace(hour=20, minute=0, second=0, microsecond=0)
    if datetime.now() > lesson_datetime_20h:
        return False

    return True
