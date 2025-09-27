from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from werkzeug.security import check_password_hash
from forms import AdminForm
from extensions import db, mail, auth
from flask_mail import Message
from functools import wraps
from models import User, Subject, Lesson, Group
from resources import DATETIME_FORMAT_JS, DATETIME_FORMAT_PY, formatTitle, get_leaderboard, secrets, log, debug_only, DEBUG, validate_form, get_free_for_date, parse_hour, safe_redirect
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
ALLOWED_GROUPS = ['y1', 'y2', 'y3', 'y4']
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

        flash("You must be an admin to access this page.", "danger")
        return redirect(url_for('views.home'))

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

        flash("You must be a tutor (or higher) to access this page.", "danger")
        return redirect(url_for('views.home'))

    return wrapper

def fake_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, context={'user': {'name': 'Debug User', 'preferred_username': 'lenart@kladnik.cc'}}, **kwargs)

    return wrapper

def login_required(func):
    """
    Rename auth.login_required to login_required
    """

    if DEBUG < 2:
        return auth.login_required(func)

    else:
        return fake_login(func)

@views.route('/new_user')
@debug_only
def new_user_debug():
    current_user({'user': { 'name': request.args.get('username'), 'preferred_username': request.args.get('email')}})

    return redirect(url_for('views.home'))

@views.route('/test_email')
@debug_only
def send_email_debug():
    sendEmail('Test', ['lenart.kladnik@gmail.com'], f'This is a test email. Sent at {datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.')

    return redirect(url_for('views.home'))

@views.route('/score/<int:sc>/<int:id>')
@debug_only
def score_debug(sc, id):
    user = User.query.filter_by(id=id).first()
    if user:
        user.score = sc
        db.session.commit()

    return redirect(url_for('views.leaderboard'))

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
            user.role = 'admin'
            db.session.commit()

            log(f"Made {user.username} ({user.email}) an administrator.", "views.requestAdmin")

            return redirect(url_for("views.adminPanel"))

        else:
            flash("Wrong password", "danger")

    return render_template("admin.html", current_user=current_user(context), form=form)

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

    if reject_potential_tutor:
        user_to_be_rejected = User.query.filter_by(id=potential_tutor_user_id).first()
        if user_to_be_rejected:
            user_to_be_rejected.tutoring_subjects = ''
            user_to_be_rejected.applied_subjects = ''
            user_to_be_rejected.rejected = 1

            db.session.commit()

            log(f"Rejected user {user_to_be_rejected.username} ({user_to_be_rejected.email}) from being a tutor.", "views.adminPanel")

    elif accept_potential_tutor:
        user_to_be_accepted = User.query.filter_by(id=potential_tutor_user_id).first()
        if user_to_be_accepted:
            subjects_for_tutor = user_to_be_accepted.get_applied_subjects()

            for subject in subjects_for_tutor:
                s = Subject.query.filter_by(name=subject).first()

                if s and not (user_to_be_accepted.username in s.get_tutors()):
                    s.tutors = ','.join(s.get_tutors() + [user_to_be_accepted.username])

            user_to_be_accepted.tutoring_subjects = user_to_be_accepted.applied_subjects
            user_to_be_accepted.applied_subjects = ''
            user_to_be_accepted.rejected = -1

            db.session.commit()

            log(f"Accepted user {user_to_be_accepted.username} ({user_to_be_accepted.email}) as a tutor.", "views.adminPanel")

            return redirect(url_for("views.adminPanel"))

    users_filtered = []
    if filter_data:
        for user in users:
            year_f = filter_data.get('year', None)
            tutor_f = filter_data.get('tutor-for', None)
            admin_f = filter_data.get('is-admin', None)

            if year_f and user.get_year() not in year_f:
                continue

            if tutor_f and len(set(tutor_f) - set(user.tutor_for(Subject))) > 0:
                continue

            if admin_f != None and user.is_admin() != admin_f:
                continue

            users_filtered.append(user)
    else:
        users_filtered = users

    all_potential_tutors = [user for user in User.query.all() if user.applied_subjects]

    return render_template("admin_panel.html", current_user=current_user(context), users_filtered=users_filtered, all_potential_tutors=all_potential_tutors, int=int, len=len, admins=admins, users=users, User=User, tutor_manage_id=tutor_manage_id, remove_user_id=remove_user_id, manage_user_id=manage_user_id, tutors=zip(list(map(lambda tutor: tutor.tutor_for(), tutors)), tutors), subjects=subjects, subject_names=[s.name for s in subjects], groups=groups, group_ids=group_ids, formatTitle=formatTitle, zip=zip, set=set, list=list)

@views.route('/modify-user/<int:id>', methods=['POST'])
@login_required
@admin_required
def modify_user(*, context, id):
    form = request.form # Treated as safe since only authorized users can access this

    if form:
        user = User.query.filter_by(id=id).first()

        if not user:
            return redirect(safe_redirect(request.referrer))

        is_admin = form.get('is-admin')
        year = form.get('year')
        tutor_for = form.getlist('tutor-for')

        if is_admin == 'on':
            user.role = 'admin'

        else:
            user.role = 'user'

        if year:
            user.groups = year

        if tutor_for:
            user.tutoring_subjects = ','.join(tutor_for)
            user.rejected = -1

            for subject in Subject.query.all():
                s = Subject.query.filter_by(name=subject.name).first()

                if not s:
                    continue

                if subject.name in tutor_for:
                    s.tutors = ','.join(list(set(s.get_tutors() + [user.username])))

                else:
                    s.tutors = ','.join(list(set(s.get_tutors()) - set([user.username])))

        db.session.commit()

    return redirect(safe_redirect(request.referrer))

@views.route('/modify-tutor/<int:id>', methods=['POST'])
@login_required
@admin_required
def modify_tutor(*, context, id):
    form = request.form # Treated as safe since only authorized users can access this

    if form:
        user = User.query.filter_by(id=id).first()

        if not user:
            return redirect(safe_redirect(request.referrer))

        tutor_for = form.getlist('tutor-for')

        if tutor_for:
            user.tutoring_subjects = ','.join(tutor_for)
            user.rejected = -1
            for subject in Subject.query.all():
                s = Subject.query.filter_by(name=subject.name).first()

                if not s:
                    continue

                if subject.name in tutor_for:
                    s.tutors = ','.join(list(set(s.get_tutors() + [user.username])))

                else:
                    s.tutors = ','.join(list(set(s.get_tutors()) - set([user.username])))

        db.session.commit()

    return redirect(safe_redirect(request.referrer))

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
                user.role = role

            elif role == 'tutor':
                subjects = list(set(request.form.getlist('subjects[]')))
                user.tutoring_subjects = ','.join(subjects)
                user.rejected = -1

                for subject in subjects:
                    s = Subject.query.filter_by(name=subject).first()

                    if s and not (user.username in s.get_tutors()):
                        s.tutors = ','.join(s.get_tutors() + [user.username])

            db.session.commit()

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
        user.role = 'user'

    elif role == 'tutor':
        if user.role != 'admin':
            user.role = 'user'

        subjects = Subject.query.filter_by().all()
        user.rejected = 1

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

    return render_template('index.html', current_user=current_user(context), lessons=lessons, subjects=subjects, subject_db=Subject, user_db=User, become_a_tutor_message=random_message)

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

def isInTimeRange(time: str, timeRange: tuple[str, str], format: str = "%H:%M") -> bool:
    time_datetime = datetime.strptime(time, format).time()
    timeRange_datetime = [datetime.strptime(i, format).time() for i in timeRange]

    return timeRange_datetime[0] <= time_datetime <= timeRange_datetime[1]

@views.route('/tutorstvo', methods=['GET', 'POST'])
@login_required
def tutorstvo(*, context):
    side = [('PRE', '7:10', '7:55'), ('O', '10:25', '10:55'), ('6', '12:40', '13:25'), ('7', '13:30', '14:15'), ('8', '14:20', '15:05')]
    free_classrooms = []
    with open(FREE_CLASSROOMS_CSV, "r") as f:
        reader = csv.reader(f)
        for i in list(reader):
            free_classrooms.append([i[0], i[1], i[2], i[3].split(',')])

    free_classrooms = str(free_classrooms).replace("'", '"')

    for lesson in Lesson.query.all():
        if datetime.strptime(lesson.datetime.split(' ')[0], DATETIME_FORMAT_JS) < datetime.today() - timedelta(days=1):
            for tutor in lesson.get_tutors():
                tutor_user = User.query.filter_by(username=tutor).first()
                if tutor_user:
                    tutor_user.score += lesson.filled

            db.session.delete(lesson)

        db.session.commit()

    if request.form and (current_user(context).is_tutor() or current_user(context).is_admin()):
        form = request.form

        if not validate_form(form,
                      ('min', lambda x: str(x).isdigit()),
                      ('max', lambda x: str(x).isdigit()),
                      ('group', lambda x: x in ALLOWED_GROUPS),
                      ('title', lambda x: Subject.query.filter_by(name = x).first() != None),
                      ('datetime', lambda x: datetime.strptime(x.split(' ')[0], DATETIME_FORMAT_JS) >= datetime.now() and any([y[1] == x.split(' ')[1] for y in side]) if x else True),
                      ('classroom', lambda x: x in get_free_for_date(datetime.strptime(form['datetime'].split(' ')[0], DATETIME_FORMAT_JS), list(free_classrooms), parse_hour(form['datetime'].split(' ')[1]))),
                      ('tutors', lambda x: (not x and current_user(context).is_tutor_for(Subject.query.filter_by(name=form['title']).first())) or any([User.query.filter_by(username=y).first().is_tutor_for(Subject.query.filter_by(name=form['title']).first()) for y in x.split(', ')]))
                            ):
            return redirect(url_for('views.tutorstvo'))

        if int(form['min']) > int(form['max']):
            return redirect(url_for('views.tutorstvo'))

        new_lesson = Lesson(
            groups=form['group'],
            subject=form['title'],
            classroom=form['classroom'],
            min=form['min'],
            max=form['max'],
            datetime=form['datetime'] or f"{datetime.now().year}/{datetime.now().day}/{datetime.now().month} 00:00",
            description=form['description'],
            tutors=', '.join([current_user(context).username] + (form['tutors'].split(', ') if form['tutors'] else []) if current_user(context).is_tutor_for(Subject.query.filter_by(name=form['title']).first()) else form['tutors'].split(', '))
        )
        print(new_lesson.tutors)
        db.session.add(new_lesson)

        db.session.commit()

    search = request.args.get('search', None)

    lessons = Lesson.query.filter(Lesson.id.notin_(current_user(context).getSelectedSubjects()))
    mask = list(map(lambda lesson: any(map(lambda x: x in current_user(context).get_groups(), lesson.get_groups())), lessons))
    lessons = [d for d, m in zip(lessons, mask) if m]

    user_agent = request.headers.get('User-Agent', '').lower()
    mobile = False
    if any(mobile in user_agent for mobile in ['iphone', 'android', 'ipad', 'mobile']):
        mobile = True

    startDate = request.args.get('date')
    if (startDate != '' and startDate) and not mobile:
        startDate = datetime.strptime(startDate, DATETIME_FORMAT_PY)
        startDate = startDate - timedelta(days=startDate.weekday())

    elif not mobile:
        startDate = datetime.today() - timedelta(days=datetime.today().weekday())

    elif not startDate or startDate == '':
        startDate = datetime.today() + timedelta(days=1)

    else:
        startDate = datetime.strptime(startDate, DATETIME_FORMAT_PY)

    lessons_by_column = []

    r = 1 if mobile else 5
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
    subjects = current_user(context).subjects(Subject)
    all_subjects = Subject.query.all()

    days_ = getWeek(startDate)
    rows = (lessons_by_row, side)

    startNext[0] = startNext[0] if datetime.strptime(startNext[0], DATETIME_FORMAT_PY) >= datetime.today() - timedelta(days=abs(7 - datetime.today().weekday())) else ''

    if mobile:
        if startDate.weekday() > 4:
            startDate = startDate + timedelta(days=abs(startDate.weekday() - 7))

        days_ = [(days[startDate.weekday()], f"{startDate.day}. {months[startDate.month]}"), days[startDate.weekday()]]
        startNext = [
                        (startDate - timedelta(days=1) if (startDate - timedelta(days=1)).weekday() <= 4 else startDate - timedelta(days=3)).strftime(DATETIME_FORMAT_PY),
                        (startDate + timedelta(days=1) if startDate.weekday() + 1 <= 4 else startDate + timedelta(days=3)).strftime(DATETIME_FORMAT_PY)
                    ]

        startNext[0] = startNext[0] if datetime.strptime(startNext[0], DATETIME_FORMAT_PY) >= datetime.today() - timedelta(days=1) else ''

    all_tutors = {}
    for subject in all_subjects:
        c_tutors = subject.get_tutors()
        if current_user(context).username in c_tutors:
            c_tutors.remove(current_user(context).username)

        all_tutors.update({subject.name: c_tutors})

    return render_template('tutorstvo.html', current_user=current_user(context), mobile=mobile, search=search, lessons=lessons, subjects=subjects, all_tutors=all_tutors, all_subjects=all_subjects, subject_db=Subject, user_db=User, days=days_, startNext=startNext, rows=rows, enumerate=enumerate, free_classrooms=free_classrooms, len=len, str=str, any=any)

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
    subjects = current_user(context).subjects(Subject)

    if not lesson or not subjects:
        return redirect(safe_redirect(request.referrer))

    if lesson.subject.lower() in subjects:
        db.session.delete(lesson)

        db.session.commit()

    else:
        print(f'{current_user(context).username} tried to delete without permissions.')

    return redirect(safe_redirect(request.referrer))

@views.route('/learning-resources')
@login_required
def learning_resources(*, context):
    subjects = Subject.query.all()

    return render_template('learning_resources.html', current_user=current_user(context), subjects=subjects)

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
    max_w = 600 - 1

    return render_template('leaderboard.html', current_user=current_user(context), lb=lb, max_w=max_w)

@views.route('/become-a-tutor', methods=["POST"])
@login_required
def become_a_tutor(*, context):
    if request.form and validate_form(request.form,
                                      ('subjects[]', lambda x: not False in [Subject.query.filter_by(name = i).first() != None for i in x]),
                                      getter="getlist"
                                     ):
        form = request.form
        subject_names = list(filter(lambda x: x != '/', set(form.getlist('subjects[]'))))
        current_user(context).applied_subjects = ', '.join(subject_names)
        db.session.commit()

    return redirect(safe_redirect(request.referrer))
