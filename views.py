import os
from collections import defaultdict
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app, g
from werkzeug.security import check_password_hash
from forms import AdminForm
from extensions import db, mail, auth
from flask_mail import Message
from functools import wraps
from models import Comment, LessonRequest, Stats, User, Subject, Lesson, Group
from resources import DATETIME_FORMAT_JS, DATETIME_FORMAT_PY, ALLOWED_GROUPS, FORM_VALIDATION_OFF, HUMAN_READABLE_GROUPS, StatTypes, formatTitle, get_leaderboard, is_mobile, is_tablet, secrets, log, debug_only, DEBUG, validate_form, validate_form_reason, get_free_for_date, parse_hour, safe_redirect, classroom_data
from datetime import datetime, timedelta
import csv
import random
import re

views = Blueprint('views', __name__)

def current_user(ctx) -> User:
    username = ctx["user"].get("name")
    email = ctx["user"].get("preferred_username")

    user = User.query.filter_by(email=email).first()

    if not user:
        new_user = User(username=username, email=email)
        db.session.add(new_user)
        db.session.commit()

        log(f"Created new user entry with {username=}, {email=}.", "views.current_user")

        user = new_user

    return user

FREE_CLASSROOMS_CSV = 'ucilnice.csv'
DEFAULT_DEBUG_USER = 'Debug User'
current_debug_user = DEFAULT_DEBUG_USER
# TESTS_DIR = 'static/tests' # Stari testi
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'} # Allowed extension for image upload
BECOME_A_TUTOR_MESSAGES = [
    "Postani del spremembe na Gimnaziji Šentvid! - Pridruži se tutorskemu programu in pomagaj sošolcem.",
    "Tvoja pomoč šteje! - Postani tutor in pomagaj drugim.",
    "Deli svoje znanje, pridobi dragocene izkušnje! - Tutorski program te čaka.",
    "Se spomniš, kako si se počutil prvi dan na gimnaziji? - Pomagaj novim učencem, da se lažje znajdejo. Postani njihov tutor!",
    "Imaš znanje, ki ga drugi potrebujejo? - Ne obdrži ga zase – deli ga kot tutor na Gimnaziji Šentvid.",
    "Gradimo močnejšo šolsko skupnost skupaj! - Vsak tutor prispeva k boljšemu vzdušju na naši šoli.",
    "Tutorstvo = korak k tvoji prihodnosti - Razvij vodstvene veščine, pridobi izkušnje in pomagaj sošolcem.",
    "Mali koraki, velike spremembe - Že z eno uro na teden lahko pomagaš nekomu do boljših ocen"
]
URL_REGEX = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"

def sendEmail(subject: str = '', recipients: list[str] | None = None, content: str = '', heading: str = ''):
    """
    Send email from the email address specified in secrets
    """

    if recipients:
        recipients = list(filter(None, recipients)) # Remove empty recipients

    else:
        recipients = []

    if recipients:
        msg = Message(
            subject=f'[Tutorstvo Gimnazija Šentvid]: {subject}',
            sender=current_app.config['MAIL_ADDRESS'],
            recipients=recipients,
            html=render_template('email.html', content=content, title=heading)
        )

        try:
            mail.send(msg)
            log(f"Sent email to {recipients=}.", "views.sendEmail")

            return ''
        except Exception as e:
            log(f"Error whilst sending email: {e}", "views.sendEmail", "error")
            return f'Error whilst sending email: {e}'

def getEmails(usernames: list[str]) -> list[str]:
    """
    Get email addresses for multiple users
    """

    emails = []
    for username in usernames:
        user = User.query.filter_by(username=username).first()
        if user:
            emails.append(user.email)

    return emails

# def isAllowedFile(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_stats(name: str):
    if not Stats.query.filter_by(name=name).first():
        new_stat = Stats(
            name=name,
        )
        db.session.add(new_stat)
        db.session.commit()

def plus_n_stats(name: str, key: str, n: int):
    stat = Stats.query.filter_by(name=name).first()
    data = defaultdict(int, stat.get())
    data[key] += n
    stat.set(dict(data))

    db.session.commit()

def set_tutor(user: str | User, subjects: list[str]):
    if isinstance(user, str):
        user = User.query.filter_by(username=user).first()

    user.tutoring_subjects = ','.join(set(subjects))

    for s in Subject.query.all():
        if s.name in subjects:
            s.tutors = ','.join(list(set(s.get_tutors() + [user.username])))

        else:
            s.tutors = ','.join(list(set(s.get_tutors()) - set([user.username])))

    db.session.commit()

def set_admin(user: str | User):
    if isinstance(user, str):
        user = User.query.filter_by(username=user).first()

    user.role = 'admin'

    db.session.commit()

def set_user(user: str | User):
    if isinstance(user, str):
        user = User.query.filter_by(username=user).first()

    user.role = 'user'

    db.session.commit()

def admin_required(func):
    """
    Decorator for functions that only a
    user logged in as an admin can access
    """

    @wraps(func)
    def wrapper(*args, context=None, **kwargs):
        if not context:
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for('views.home'))

        user = current_user(context)
        if user.is_admin():
            log(f"Admin route accessed by {user.username} ({user.email}).", "views.admin_required")
            return func(*args, context=context, **kwargs)

        return render_template("404.html")

    return wrapper

def tutor_required(func):
    """
    Decorator for functions that only a
    user logged in as a tutor (or higher)
    can access
    """

    @wraps(func)
    def wrapper(*args, context=None, **kwargs):
        if not context:
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for('views.home'))

        if current_user(context).is_admin() or current_user(context).is_tutor():
            return func(*args, context=context, **kwargs)

        return render_template("404.html")

    return wrapper

def fake_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        name = current_debug_user
        email = f'{current_debug_user.replace(' ', '_')}@example.com'

        current_user({'user': { 'name': name, 'preferred_username': email}})

        g.context = {'user': {'name': name, 'preferred_username': email}}

        return func(*args, context={'user': {'name': name, 'preferred_username': email}}, **kwargs)

    return wrapper

def login(func):
    if DEBUG < 2:
        return auth.login_required(func)

    else:
        return fake_login(func)

def login_required(func):
    """
    Rename auth.login_required to login_required and add debug functionality.
    Add user blocking functionality.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        context = kwargs.get('context')
        g.context = context
        user = current_user(context)
        if user.is_rejected() and user.rejection_expired():
            user.accept()
            db.session.commit()

        elif user.issues >= 2:
            if not user.is_rejected():
                user.reject()
                db.session.commit()

            return render_template("forbidden.html", current_user=user)

        today = datetime.today()
        if not user.updated_year and today.month == 9 and today.day == 1:
            ensure_stats(StatTypes.best_tutors)
            stat = Stats.query.filter_by(name=StatTypes.best_tutors).first()
            stat.value.set(list(get_leaderboard(User, Subject))[:10])
            stat.year = f"{datetime.now().year - 1}/{datetime.now().year}"

            full_year = user.get_year()
            if len(full_year) > 1 and full_year[1].isdigit():
                y = int(full_year[1]) + 1
                if y <= 4:
                    user.groups = f'y{y}'
                user.updated_year = True

            user.points = 0

            db.session.commit()

        if user.updated_year and today.month == 9 and today.day == 2:
            user.updated_year = False

            db.session.commit()

        return func(*args, **kwargs)

    return login(wrapper)

@views.route('/new_user')
@debug_only
def new_user_debug():
    current_user({'user': { 'name': request.args.get('username'), 'preferred_username': request.args.get('email')}})

    return redirect(url_for('views.home'))

@views.route('/switch_user')
@debug_only
def switch_user_debug():
    global current_debug_user

    current_debug_user = request.args.get('username')

    return redirect(url_for('views.home'))

@views.route('/test_email')
@debug_only
def send_email_debug():
    sendEmail('Test', ['lenart@kladnik.cc'], f'This is a test email. Sent at {datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.')

    return redirect(url_for('views.home'))

@views.route('/score/<int:sc>/<int:id>')
@debug_only
def score_debug(sc, id):
    user = User.query.filter_by(id=id).first()
    if user:
        user.score = sc
        db.session.commit()

    return redirect(url_for('views.leaderboard'))

@views.route('/new_lesson')
@debug_only
def new_lesson_debug():
    new_lesson = Lesson(
            groups="y2",
            subject="Matematika",
            classroom="msv",
            min="1",
            max="2",
            datetime=f"{datetime.now().year}/{datetime.now().day + 1}/{datetime.now().month} 00:00",
            description="debug lesson",
            tutors='Test'
        )
    db.session.add(new_lesson)

    db.session.commit()

    return redirect(url_for('views.tutorstvo'))

@views.route('/cause_exc')
@debug_only
def cause_exc():
    raise RuntimeError("Example exception.")

@views.route('/')
@login_required
def index(*, context):
    return redirect(url_for('views.home'))

@views.route('/toggle-dark-mode')
@login_required
def toggleDarkMode(*, context):
    current_user(context).dark_mode = not current_user(context).dark_mode
    db.session.commit()

    return redirect(safe_redirect(request.referrer))

@views.route("/logout")
@login_required
def logout(*, context):
    return redirect(url_for('identity.logout'))

@views.route('/admin', methods=['GET', 'POST'])
@login_required
def requestAdmin(*, context):
    form = AdminForm()
    if form.validate_on_submit():
        hash = secrets['admin-password']

        if check_password_hash(hash, form.password.data):
            user = current_user(context)
            set_admin(user)
            db.session.commit()

            log(f"Made {user.username} ({user.email}) an administrator.", "views.requestAdmin")

            return redirect(url_for("views.adminPanel"))

        else:
            flash("Wrong password", "danger")

    return render_template("admin.html", current_user=current_user(context), mobile=is_mobile(request), form=form)

@views.route('/run-update')
@login_required
@admin_required
def run_update(*, context):
    os.system('/update.sh')

    return redirect(safe_redirect(request.referrer))

@views.route('/admin-panel', methods=['GET', 'POST'])
@login_required
@admin_required
def adminPanel(*, context):
    if request.method == 'POST':
        form = request.form # Treated as safe since only authorized users can access this

        session['manage_user_id'] = form.get('manage_user_id')
        session['remove_user_id'] = form.get('remove_user_id')
        session['potential_tutor_user_id'] = form.get('potential_tutor_user_id')
        session['tutor_manage_id'] = form.get('tutor_manage_id')
        session['reject_potential_tutor'] = form.get('reject_from_tutor.x')
        session['accept_potential_tutor'] = form.get('accept_as_tutor.x')
        session['block_potential_tutor'] = form.get('block_from_tutor.x')

        filter_data = {}
        if form.get('filter-include-year'):
            filter_data.update({'year': form.getlist('filter-year')})

        if form.get('filter-include-tutor'):
            filter_data.update({'tutor-for': form.getlist('filter-tutor-for')})

        if form.get('filter-include-other'):
            filter_data.update({'is-admin': form.get('filter-is-admin') == 'on'})

        session['filter_data'] = filter_data

        return redirect(url_for('views.adminPanel'))

    admins = User.query.filter_by(role="admin").all()
    tutors = [user for user in User.query.all() if user.is_tutor()]
    subjects = Subject.query.all()
    groups = [group.name for group in Group.query.all()]
    group_ids = [group.id for group in Group.query.all()]
    users = User.query.all()

    manage_user_id = session.pop('manage_user_id', None)
    remove_user_id = session.pop('remove_user_id', None)
    tutor_manage_id = session.pop('tutor_manage_id', None)
    filter_data = session.pop('filter_data', None)
    potential_tutor_user_id = session.pop('potential_tutor_user_id', None)
    reject_potential_tutor = session.pop('reject_potential_tutor', None)
    accept_potential_tutor = session.pop('accept_potential_tutor', None)
    block_potential_tutor = session.pop('block_potential_tutor', None)

    if reject_potential_tutor:
        user_to_be_rejected = User.query.filter_by(id=potential_tutor_user_id).first()
        if user_to_be_rejected:
            user_to_be_rejected.tutoring_subjects = ''
            user_to_be_rejected.applied_subjects = ''
            user_to_be_rejected.tutor = -1

            db.session.commit()

            log(f"Rejected user {user_to_be_rejected.username} ({user_to_be_rejected.email}) from being a tutor.", "views.adminPanel")

    elif block_potential_tutor:
        user_to_be_rejected = User.query.filter_by(id=potential_tutor_user_id).first()
        if user_to_be_rejected:
            user_to_be_rejected.tutoring_subjects = ''
            user_to_be_rejected.applied_subjects = ''
            user_to_be_rejected.reject()

            db.session.commit()

            log(f"Blocked user {user_to_be_rejected.username} ({user_to_be_rejected.email}) from ever becoming a tutor.", "views.adminPanel")

    elif accept_potential_tutor:
        user_to_be_accepted = User.query.filter_by(id=potential_tutor_user_id).first()
        if user_to_be_accepted:
            subjects_for_tutor = user_to_be_accepted.get_applied_subjects()

            set_tutor(user_to_be_accepted, subjects_for_tutor)

            user_to_be_accepted.applied_subjects = ''
            user_to_be_accepted.tutor = 1

            db.session.commit()

            log(f"Accepted user {user_to_be_accepted.username} ({user_to_be_accepted.email}) as a tutor.", "views.adminPanel")

            return redirect(url_for("views.adminPanel"))

    users_filtered = []
    if filter_data:
        for user in users:
            year_f = filter_data.get('year', None)
            tutor_f = filter_data.get('tutor-for', [])
            admin_f = filter_data.get('is-admin', None)

            if year_f and user.get_year() not in year_f:
                continue

            if tutor_f and not any([s in user.get_tutoring_subjects() for s in tutor_f]):
                continue

            if admin_f != None and user.is_admin() != admin_f:
                continue

            users_filtered.append(user)
    else:
        users_filtered = users

    all_potential_tutors = [user for user in User.query.all() if user.applied_subjects]

    tutors_zip = list(zip(list(map(lambda tutor: tutor.tutor_for(), tutors)), tutors))

    return render_template("admin_panel.html",
                           current_user=current_user(context),
                           mobile=is_mobile(request),
                           users_filtered=users_filtered,
                           all_potential_tutors=all_potential_tutors, int=int,
                           len=len, admins=admins, users=users, User=User,
                           tutor_manage_id=tutor_manage_id,
                           remove_user_id=remove_user_id,
                           manage_user_id=manage_user_id,
                           tutors=tutors_zip, tutors_len=len(tutors_zip),
                           subjects=subjects,
                           subject_names=[s.name for s in subjects], groups=groups, group_ids=group_ids,
                           formatTitle=formatTitle, zip=zip, set=set,
                           list=list)

@views.route('/modify-user/<int:id>', methods=['POST'])
@login_required
@admin_required
def modify_user(*, context, id):
    form = request.form # Treated as safe since only authorized users can access this

    user = User.query.filter_by(id=id).first()

    if not user:
        return redirect(url_for('views.adminPanel'))

    is_admin = form.get('is-admin', 'off')
    year = form.get('year', None)
    tutor_for = list(set(form.getlist('tutor-for')))
    score = form.get('points', None)

    if is_admin == 'on':
        set_admin(user)

    else:
        set_user(user)

    if year:
        user.groups = year

    set_tutor(user, tutor_for)

    if score:
        user.score = score

    db.session.commit()

    return redirect(url_for('views.adminPanel'))

@views.route('/modify-tutor/<int:id>', methods=['POST'])
@login_required
@admin_required
def modify_tutor(*, context, id):
    form = request.form # Treated as safe since only authorized users can access this

    user = User.query.filter_by(id=id).first()

    if not user:
        return redirect(url_for('views.adminPanel'))

    tutor_for = list(set(form.getlist('tutor-for')))

    set_tutor(user, tutor_for)

    db.session.commit()

    return redirect(url_for('views.adminPanel'))

@views.route('/modify-lesson/<int:id>')
@login_required
@admin_required
def modify_lesson(*, context, id):
    lesson = Lesson.query.filter_by(id=id).first()

    return f"""{lesson.id=}
    <br />
    {lesson.groups=}
    <br />
    {lesson.subject=}
    <br />
    {lesson.classroom=}
    <br />
    {lesson.min=}
    <br />
    {lesson.max=}
    <br />
    {lesson.datetime=}
    <br />
    {lesson.description=}
    <br />
    {lesson.filled=}
    <br />
    {lesson.tutors=}
    <br />
    {lesson.passed=}
    <br />"""

@views.route('/remove-user/<int:id>')
@login_required
@admin_required
def remove_user(*, context, id):
    # Treated as safe since only authorized users can access this
    user = User.query.filter_by(id=id).first()

    if not user:
        return redirect(safe_redirect(request.referrer))

    uname = user.username
    email = user.email

    db.session.delete(user)

    db.session.commit()

    log(f"Remove user {uname} ({email}).", "views.remove_user")

    return redirect(safe_redirect(request.referrer))

@views.route('/add-subject', methods=['GET', 'POST'])
@login_required
@admin_required
def addSubject(*, context):
    if request.form: # Treated as safe since only authorized users can access this
        name = request.form['name'].lower()

        if not Subject.query.filter_by(name=name).first():
            new_subject = Subject(name=name, tutors='')
            db.session.add(new_subject)

            db.session.commit()

    return redirect(safe_redirect(request.referrer))

@views.route('/remove-subject/<name>')
@login_required
@admin_required
def removeSubject(*, context, name):
    # Treated as safe since only authorized users can access this
    subject = Subject.query.filter_by(name=name).first()
    db.session.delete(subject)

    db.session.commit()

    return redirect(safe_redirect(request.referrer))

@views.route('/add-group', methods=['POST'])
@login_required
@admin_required
def addGroup(*, context):
    if request.form: # Treated as safe since only authorized users can access this
        name = request.form['name']

        try:
            new_group = Group(name=name)
            db.session.add(new_group)

            db.session.commit()
        except:
            pass

    return redirect(safe_redirect(request.referrer))

@views.route('/remove-group/<id>')
@login_required
@admin_required
def removeGroup(*, context, id):
    # Treated as safe since only authorized users can access this
    group = Group.query.filter_by(id=id).first()
    db.session.delete(group)

    db.session.commit()

    return redirect(safe_redirect(request.referrer))

@views.route('/add-to-group',  methods=['POST'])
@login_required
@admin_required
def addToGroup(*, context):
    if request.form: # Treated as safe since only authorized users can access this
        groups = request.form.getlist('groups[]')
        username = request.form['username']

        user = User.query.filter_by(username=username).first()

        if not user:
            return redirect(safe_redirect(request.referrer))

        user.groups = ','.join(groups)

        db.session.commit()

    return redirect(safe_redirect(request.referrer))

@views.route('/add-role/<role>', methods=['POST'])
@login_required
@admin_required
def addRole(*, context, role):
    if request.form: # Treated as safe since only authorized users can access this
        username = request.form['username']

        user = User.query.filter_by(username=username).first()

        if user:
            if role == 'admin':
                set_admin(user)

            elif role == 'tutor':
                set_tutor(user, list(set(user.get_tutoring_subjects() + request.form.getlist('subjects[]'))))

        else:
            flash('There is no user with that name.', 'danger')

    return redirect(safe_redirect(request.referrer))

@views.route('/remove-role/<role>/<int:id>')
@login_required
@admin_required
def removeRole(*, context, role, id):
    # Treated as safe since only authorized users can access this
    user = User.query.filter_by(id=id).first()

    if not user:
        return redirect(safe_redirect(request.referrer))

    if role == 'admin':
        set_user(user)

    elif role == 'tutor':
        if user.role != 'admin':
            set_user(user)

        subjects = Subject.query.filter_by().all()
        user.tutoring_subjects = ''

        for s in subjects:
            if user.username in s.get_tutors():
                s.tutors = ','.join(set(s.get_tutors()) - {user.username})

    db.session.commit()

    return redirect(safe_redirect(request.referrer))

@views.route('/home')
@login_required
def home(*, context):
    lessons = Lesson.query.filter(Lesson.id.in_(current_user(context).getSelectedSubjects()))
    subjects = Subject.query.filter_by().all()

    msg = random.randrange(0, len(BECOME_A_TUTOR_MESSAGES))
    random_message = BECOME_A_TUTOR_MESSAGES[msg].split(' - ')

    return render_template('index.html', current_user=current_user(context), mobile=is_mobile(request), lessons=lessons, subjects=subjects, subject_db=Subject, user_db=User, become_a_tutor_message=random_message)

months = {
    1: 'Januar',
    2: 'Februar',
    3: 'Marec',
    4: 'April',
    5: 'Maj',
    6: 'Junij',
    7: 'Julij',
    8: 'Avgust',
    9: 'September',
    10: 'Oktober',
    11: 'November',
    12: 'December'
}

days = {
    0: 'ponedeljek',
    1: 'torek',
    2: 'sreda',
    3: 'četrtek',
    4: 'petek',
    5: 'sobota',
    6: 'nedelja'
}

def getWeek(start_date: datetime) -> tuple[list[tuple], str]:
    weekStart = start_date - timedelta(days=start_date.weekday())

    week = []
    for i in range(5):
        day = weekStart + timedelta(days=i)
        week.append((days[day.weekday()], f"{day.day}. {months[day.month]}"))

    return week, days[start_date.weekday()]

def nextWeekDates(start_date: datetime, n: int) -> tuple[list[tuple], str]:
    days_ = []

    i = 0
    of = 1

    while i < n:
        d = start_date + timedelta(days=of)
        if d.weekday() < 5:
            days_.append((days[d.weekday()], f"{d.day} {months[d.month]}"))

            i += 1

        of += 1

    return days_, days[start_date.weekday()]

def isInTimeRange(time: str, timeRange: tuple[str, str], format: str = "%H:%M") -> bool:
    time_datetime = datetime.strptime(time, format).time()
    timeRange_datetime = [datetime.strptime(i, format).time() for i in timeRange]

    return timeRange_datetime[0] <= time_datetime <= timeRange_datetime[1]

@views.route('/tutorstvo', methods=['GET', 'POST'])
@login_required
def tutorstvo(*, context):
    side = [('PRE', '7:10', '7:55'), ('O', '10:25', '10:55'), ('6', '12:40', '13:25'), ('7', '13:30', '14:15'), ('8', '14:20', '15:05'), ('PO', '15:10', '23:59')]

    free_classrooms = []
    classroom_csv_placeholder = 'A,Ponedeljek,1,""\nA,Ponedeljek,2,""\nA,Ponedeljek,3,""\nA,Ponedeljek,4,""\nA,Ponedeljek,5,""\nA,Ponedeljek,6,""\nA,Ponedeljek,7,""\nA,Torek,1,""\nA,Torek,2,""\nA,Torek,3,""\nA,Torek,4,""\nA,Torek,5,""\nA,Torek,6,""\nA,Torek,7,""\nA,Sreda,1,""\nA,Sreda,2,""\nA,Sreda,3,""\nA,Sreda,4,""\nA,Sreda,5,""\nA,Sreda,6,""\nA,Sreda,7,""\nA,četrtek,1,""\nA,četrtek,2,""\nA,četrtek,3,""\nA,četrtek,4,""\nA,četrtek,5,""\nA,četrtek,6,""\nA,četrtek,7,""\nA,Petek,1,""\nA,Petek,2,""\nA,Petek,3,""\nA,Petek,4,""\nA,Petek,5,""\nA,Petek,6,""\nA,Petek,7,""\nB,Ponedeljek,1,""\nB,Ponedeljek,2,""\nB,Ponedeljek,3,""\nB,Ponedeljek,4,""\nB,Ponedeljek,5,""\nB,Ponedeljek,6,""\nB,Ponedeljek,7,""\nB,Torek,1,""\nB,Torek,2,""\nB,Torek,3,""\nB,Torek,4,""\nB,Torek,5,""\nB,Torek,6,""\nB,Torek,7,""\nB,Sreda,1,""\nB,Sreda,2,""\nB,Sreda,3,""\nB,Sreda,4,""\nB,Sreda,5,""\nB,Sreda,6,""\nB,Sreda,7,""\nB,četrtek,1,""\nB,četrtek,2,""\nB,četrtek,3,""\nB,četrtek,4,""\nB,četrtek,5,""\nB,četrtek,6,""\nB,četrtek,7,""\nB,Petek,1,""\nB,Petek,2,""\nB,Petek,3,""\nB,Petek,4,""\nB,Petek,5,""\nB,Petek,6,""\nB,Petek,7,""'

    reader_list = []
    for i in classroom_csv_placeholder.split('\n'):
        reader_list.append(i.split(','))

    if os.path.exists(FREE_CLASSROOMS_CSV):
        with open(FREE_CLASSROOMS_CSV, "r") as f:
            reader = csv.reader(f)

            reader_list = []
            for i in list(reader):
                reader_list.append(i)

    for i in reader_list:
        free_classrooms.append([i[0], i[1], i[2], i[3].split(',') if i[3].strip() and i[3].strip() != '""' else []])

    free_classrooms = str(free_classrooms).replace("'", '"')

    for lesson in Lesson.query.all():
        if datetime.strptime(lesson.datetime.split(' ')[0], DATETIME_FORMAT_JS) < datetime.today() - timedelta(days=1) and not lesson.has_passed():
            for tutor in lesson.get_tutors():
                tutor_user = User.query.filter_by(username=tutor).first()
                if tutor_user:
                    tutor_user.score += lesson.filled

            ensure_stats(StatTypes.attendees)
            plus_n_stats(StatTypes.attendees, lesson.subject.lower(), lesson.filled)

            lesson.set_passed()

        if datetime.strptime(lesson.datetime.split(' ')[0], DATETIME_FORMAT_JS) < datetime.today() - timedelta(days=7):
            db.session.delete(lesson)

        db.session.commit()

    lesson_creation_error = None

    if request.form and (current_user(context).is_tutor()):
        form = request.form

        validation_result = validate_form_reason(form,
                      ('min', lambda x: str(x).isdigit()),
                      ('max', lambda x: str(x).isdigit()),
                      ('groups', lambda x: not any([i not in current_user(context).tutoring_years() for i in x.split(',')]) and x),
                      ('title', lambda x: Subject.query.filter_by(name = x).first() != None),
                      ('datetime', lambda x: datetime.strptime(x.split(' ')[0], DATETIME_FORMAT_JS) >= datetime.now() and any([y[1] == x.split(' ')[1] for y in side]) if x else True),
                      # ('classroom', lambda x: x in get_free_for_date(datetime.strptime(form['datetime'].split(' ')[0], DATETIME_FORMAT_JS), list(free_classrooms), parse_hour(form['datetime'].split(' ')[1]))),
                      ('classroom', lambda x: x in get_free_for_date(parse_hour(form['datetime'].split(' ')[1]))),
                      ('tutors', lambda x: (current_user(context).is_tutor_for(Subject.query.filter_by(name=form['title']).first())) and any([User.query.filter_by(username=y).first().is_tutor_for(Subject.query.filter_by(name=form['title']).first()) for y in x.split(', ')]) if x else True),
                      ('datetime', lambda x: (not any(i.subject.lower() == form['title'].lower() for i in Lesson.query.filter_by(datetime=x)))),
                      ('tutors', lambda _: (not any(any(j in ([current_user(context).username] + (form['tutors'].split(', ') if form['tutors'] else []) if current_user(context).is_tutor_for(Subject.query.filter_by(name=form['title']).first()) else form['tutors'].split(', ')) for j in i.get_tutors()) for i in Lesson.query.filter_by(datetime=form['datetime'])))),
                      ('classroom', lambda x: (not any(i.classroom == x for i in Lesson.query.filter_by(datetime=form['datetime'])))),
                        )

        if not validation_result[0]:
            return redirect(safe_redirect(request.referrer))

        if int(form['min']) > int(form['max']):
            return redirect(safe_redirect(request.referrer))

        new_lesson = Lesson(
            groups=form['groups'],
            subject=form['title'],
            classroom=form['classroom'],
            min=form['min'],
            max=form['max'],
            datetime=form['datetime'] or f"{datetime.now().year}/{datetime.now().day}/{datetime.now().month} 00:00",
            description=form['description'],
            tutors=', '.join([current_user(context).username] + (form['tutors'].split(', ') if form['tutors'] else []) if current_user(context).is_tutor_for(Subject.query.filter_by(name=form['title']).first()) else form['tutors'].split(', '))
        )
        db.session.add(new_lesson)

        ensure_stats(StatTypes.lessons_created)
        plus_n_stats(StatTypes.lessons_created, form['title'].lower(), 1)

        db.session.commit()

    search = request.args.get('search', None)

    lessons = Lesson.query.filter(Lesson.id.notin_(current_user(context).getSelectedSubjects()))
    if not current_user(context).is_admin():
        mask = list(map(lambda lesson: any(map(lambda x: x in current_user(context).get_groups() or current_user(context).username in lesson.get_tutors(), lesson.get_groups())), lessons))
        lessons = [d for d, m in zip(lessons, mask) if m]

    mobile = is_mobile(request)
    tablet = is_tablet(request)

    startDate = request.args.get('date')
    if (startDate != '' and startDate) and not mobile and not tablet:
        startDate = datetime.strptime(startDate, DATETIME_FORMAT_PY)
        startDate = startDate - timedelta(days=startDate.weekday())

    elif not mobile and not tablet:
        startDate = datetime.today() - timedelta(days=datetime.today().weekday())

    elif not startDate or startDate == '':
        startDate = datetime.today() + timedelta(days=1)

        if startDate.weekday() > 4:
            startDate += timedelta(days=startDate.weekday() - 3)

        print(startDate)

    else:
        startDate = datetime.strptime(startDate, DATETIME_FORMAT_PY)

    lessons_by_column = []

    r = 1 if mobile else 2 if tablet else 5
    for idx in range(r):
        column = []
        column_lessons = list(
            filter(
                lambda lesson:
                lesson.datetime.split(' ')[0] == (startDate + timedelta(days=idx)).strftime(DATETIME_FORMAT_JS),
                lessons
            )
        )

        for j in side:
            same_h = []
            lesson_date = f'{(startDate + timedelta(days=idx)).strftime(DATETIME_FORMAT_JS)} {j[1]}'

            for lesson in column_lessons:
                if isInTimeRange(lesson.datetime.split(' ')[1], (j[1], j[2])):
                    same_h.append((lesson_date, lesson))

            same_h.append((lesson_date, ''))
            column.append(same_h)

        lessons_by_column.append(column)

    lessons_by_row_raw = [list(x) for x in zip(*lessons_by_column)]
    lessons_by_row = []
    for data in lessons_by_row_raw:
        max_len = len(max(data, key=len))
        lessons_by_row.append((max_len, data))

    startNext = [(startDate - timedelta(days=7)).strftime(DATETIME_FORMAT_PY), (startDate + timedelta(days=7)).strftime(DATETIME_FORMAT_PY)]
    show_arrow = datetime.strptime(startNext[0], DATETIME_FORMAT_PY) >= datetime.today() - timedelta(days=abs(14 - datetime.today().weekday()))
    subjects = current_user(context).subjects(Subject)
    all_subjects = Subject.query.all()

    days_ = getWeek(startDate)
    rows = (lessons_by_row, side)

    startNext[0] = startNext[0] if datetime.strptime(startNext[0], DATETIME_FORMAT_PY) >= datetime.today() - timedelta(days=abs(7 - datetime.today().weekday())) else ''

    if mobile:
        if startDate.weekday() > 4:
            startDate = startDate + timedelta(days=abs(startDate.weekday() - 7))

        days_ = [[[days[startDate.weekday()], f"{startDate.day} {months[startDate.month]}"]]]
        startNext = [
                        (startDate - timedelta(days=1) if (startDate - timedelta(days=1)).weekday() <= 4 else startDate - timedelta(days=3)).strftime(DATETIME_FORMAT_PY),
                        (startDate + timedelta(days=1) if startDate.weekday() + 1 <= 4 else startDate + timedelta(days=3)).strftime(DATETIME_FORMAT_PY)
                    ]

        startNext[0] = startNext[0] if datetime.strptime(startNext[0], DATETIME_FORMAT_PY) >= datetime.today() - timedelta(days=4) else ''

    elif tablet:
        days_ = nextWeekDates(startDate, 2)
        startNext = [
                        (startDate - timedelta(days=2) if (startDate - timedelta(days=2)).weekday() <= 4 else startDate - timedelta(days=4)).strftime(DATETIME_FORMAT_PY),
                        (startDate + timedelta(days=2) if startDate.weekday() + 2 <= 4 else startDate + timedelta(days=4)).strftime(DATETIME_FORMAT_PY)
                    ]

        startNext[0] = startNext[0] if datetime.strptime(startNext[0], DATETIME_FORMAT_PY) >= datetime.today() - timedelta(days=4) else ''

    all_tutors = {}
    for subject in all_subjects:
        c_tutors = subject.get_tutors()
        if current_user(context).username in c_tutors:
            c_tutors.remove(current_user(context).username)

        all_tutors.update({subject.name: c_tutors})

    if FORM_VALIDATION_OFF:
        has_passed = lambda _: False
    else:
        has_passed = lambda date: datetime.strptime(date.split(' ')[0], DATETIME_FORMAT_JS) < datetime.today() - timedelta(days=1)

    return render_template('tutorstvo.html',
                           current_user=current_user(context), mobile=mobile,
                           search=search, lessons=lessons, subjects=subjects,
                           all_tutors=all_tutors, all_subjects=all_subjects,
                           subject_db=Subject, user_db=User, days=days_,
                           startNext=startNext, rows=rows, enumerate=enumerate,
                           free_classrooms=free_classrooms,
                           show_arrow=show_arrow, len=len, str=str, any=any,
                           classroom_data=classroom_data,
                           lesson_creation_error=lesson_creation_error,
                           human_readable_groups=HUMAN_READABLE_GROUPS,
                           has_passed=has_passed, tablet=tablet)

@views.route('/tutorstvo/add/<int:id>')
@login_required
def selectLesson(*, context, id):
    lesson = Lesson.query.filter_by(id=id).first()

    if lesson and not (current_user(context).username in lesson.get_tutors()) and not (lesson.filled >= lesson.max):
        current_user(context).selected_subjects = ','.join(set(current_user(context).getSelectedSubjects() + [str(id)]))

        lesson.filled += 1

        if lesson.filled == lesson.min:
            addr = list(filter(None, getEmails(lesson.get_tutors())))

            if addr:
                sendEmail(f'{lesson.subject}', addr, f"""Pozdravljeni,

        Za predmet {lesson.subject} je število učencev preseglo minimalno mejo. To pomeni da se bo ura odvijala.""", f'Tutorstvo - {lesson.subject}')

        db.session.commit()

        return redirect(url_for('views.home'))

    return redirect(safe_redirect(request.referrer))

@views.route('/tutorstvo/remove/<int:id>')
@login_required
def deselectLesson(*, context, id):
    lesson = Lesson.query.filter_by(id=id).first()
    selected = current_user(context).getSelectedSubjects()

    if not lesson.is_removable():
        return redirect(safe_redirect(request.referrer))

    if lesson:
        current_user(context).selected_subjects = ','.join(set(selected) - set(str(id)))

        lesson.filled -= 1

        if lesson.filled == lesson.min - 1:
            addr = list(filter(None, getEmails(lesson.get_tutors())))

            if addr:
                sendEmail(f'{lesson.subject}', addr, f"""Pozdravljeni,

        Za predmet {lesson.subject} je število učencev spet padlo pod minimalno mejo. To pomeni da se ura ne bo odvijala.""", f'Tutorstvo - {lesson.subject}')

        db.session.commit()

        return redirect(url_for('views.home'))

    return redirect(safe_redirect(request.referrer))

@views.route('/remove-lesson/<int:id>')
@login_required
@tutor_required
def removeLesson(*, context, id):
    lesson = Lesson.query.filter_by(id=id).first()
    if not lesson.is_removable():
        return redirect(safe_redirect(request.referrer))

    subjects = current_user(context).subjects(Subject)

    if not lesson or not subjects:
        return redirect(safe_redirect(request.referrer))

    if lesson.subject in subjects:
        for user in lesson.get_users(User):
            user.selected_subjects = ','.join(set(user.getSelectedSubjects()) - set(str(lesson.id)))

        ensure_stats(StatTypes.lessons_created)
        plus_n_stats(StatTypes.lessons_created, lesson.subject.lower(), -1)

        db.session.delete(lesson)

        db.session.commit()

    else:
        print(f'{current_user(context).username} tried to delete without permissions.')

    return redirect(safe_redirect(request.referrer))

@views.route('/learning-resources')
@login_required
def learning_resources(*, context):
    subjects = Subject.query.all()

    return render_template('learning_resources.html', current_user=current_user(context), mobile=is_mobile(request), subjects=subjects)

@views.route('/add-learning-resource', methods=['POST'])
@login_required
@tutor_required
def add_learning_resource(*, context):
    if request.form and validate_form(request.form,
                                      ('subject', lambda x: Subject.query.filter_by(name = x).first() != None),
                                      ('url', lambda x: re.fullmatch(URL_REGEX, x) != None)
                                     ):
        subject_name = request.form['subject']
        url = request.form['url']

        subject = Subject.query.filter_by(name=subject_name).first()

        if not subject:
            return redirect(safe_redirect(request.referrer))

        if current_user(context).is_tutor_for(subject):
            subject.learning_resources = ','.join(set(subject.get_learning_resources() + [url]))

            db.session.commit()

    return redirect(safe_redirect(request.referrer))

@views.route('/remove-learning-resource')
@login_required
@tutor_required
def remove_learning_resource(*, context):
    url = request.args.get('url', None)
    subject_name = request.args.get('subject', None)
    if validate_form(request.args,
            ('subject', lambda x: Subject.query.filter_by(name = x).first() != None),
            ('url', lambda x: re.fullmatch(URL_REGEX, x) != None),
            getter="get"
        ):
        subject = Subject.query.filter_by(name=subject_name).first()

        if not subject:
            return redirect(safe_redirect(request.referrer))

        if current_user(context).is_tutor_for(subject) or current_user(context).is_admin():
            subject.learning_resources = ','.join(set(subject.get_learning_resources()) - set([url]))

            db.session.commit()

    return redirect(safe_redirect(request.referrer))

@views.route('/select-group', methods=["POST"])
@login_required
def select_group(*, context):
    form = request.form

    if form and validate_form(form, ('group', lambda x: x in ALLOWED_GROUPS), getter="get"):
        group = form.get('group')
        current_user(context).groups = group
        db.session.commit()

    return redirect(safe_redirect(request.referrer))

@views.route('/leaderboard')
@login_required
def leaderboard(*, context):
    lb = get_leaderboard(User, Subject)

    return render_template('leaderboard.html', current_user=current_user(context), mobile=is_mobile(request), lb=lb)

@views.route('/become-a-tutor', methods=["POST"])
@login_required
def become_a_tutor(*, context):
    if request.form and validate_form(request.form,
                                      ('subjects[]', lambda x: not False in [Subject.query.filter_by(name = i).first() != None or i == "/" for i in x]),
                                      getter="getlist"
        ) and not current_user(context).is_rejected():
        form = request.form
        subject_names = list(filter(lambda x: x != '/', set(form.getlist('subjects[]'))))
        current_user(context).applied_subjects = ', '.join(subject_names)
        db.session.commit()

    return redirect(safe_redirect(request.referrer))

@views.route('/new_issue', methods=["POST"])
@login_required
@tutor_required
def new_issue(*, context):
    if not validate_form(request.form,
                         ('id', lambda x: Lesson.query.filter_by(id=x[0]).first() != None),
                         ('users[]', lambda x: not any([not (i == '/' or User.query.filter_by(username=i).first() in Lesson.query.filter_by(id=request.form['id']).first().get_users(User)) for i in x])),
                         getter='getlist'
                         ):
        return redirect(safe_redirect(request.referrer))

    users = [User.query.filter_by(username=i).first() if i != '/' else '' for i in request.form.getlist('users[]')]

    ensure_stats(StatTypes.reported_users)
    stat = Stats.query.filter_by(name=StatTypes.reported_users)

    exists = False
    for user in users:
        if user:
            user.issues += 1
            exists = True

            data = defaultdict(lambda: defaultdict(int), {k: defaultdict(int, v) for k, v in stat.get().items()})
            data[Lesson.query.filter_by(id=request.form['id']).first().subject.lower()][user.username] += 1
            stat.set({k: dict(v) for k, v in data.items()})

    if exists:
        db.session.delete(Lesson.query.filter_by(id=request.form['id']).first())

        db.session.commit()

    return redirect(safe_redirect(request.referrer))

@views.route('/request-lesson', methods=["GET", "POST"])
@login_required
def request_lesson(*, context):
    if request.form and validate_form(request.form,
                         ('subject', lambda x: Subject.query.filter_by(name=x).first() != None),
                         ('comment', lambda x: len(x) <= 34),
        ):
        if not LessonRequest.query.filter_by(subject=request.form["subject"]).first():
            db.session.add(LessonRequest(subject=request.form['subject']))
            db.session.commit()

        if not LessonRequest.query.filter_by(subject=request.form["subject"]).first().exists_user_entry(current_user(context).username):
            lesson_request = LessonRequest.query.filter_by(subject=request.form['subject']).first()
            new_comment = Comment(
                content=request.form['comment'] + ", " + current_user(context).human_readable_year(),
                lesson_request=lesson_request,
                by=current_user(context).username
            )

            ensure_stats(StatTypes.lesson_requests)
            plus_n_stats(StatTypes.lesson_requests, request.form['subject'], 1)

            db.session.add(new_comment)
            db.session.commit()

    for lesson_request in LessonRequest.query.all():
        for comment in lesson_request.comments:
            if comment.passed():
                db.session.delete(comment)

    db.session.commit()

    return render_template('request_lesson.html', current_user=current_user(context), mobile=is_mobile(request), subjects=Subject.query.all(), lesson_request_db=LessonRequest)

@views.route("/faq")
@login_required
def faq(*, context):
    return render_template("faq.html", current_user=current_user(context), mobile=is_mobile(request))
