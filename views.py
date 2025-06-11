from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import check_password_hash
from forms import AdminForm
from extensions import db, mail, auth
from flask_mail import Message
from functools import wraps
from models import User, Subject, Lesson, Group
from resources import DATETIME_FORMAT_JS, DATETIME_FORMAT_PY, formatTitle, secrets
from datetime import datetime, timedelta
import csv

views = Blueprint('views', __name__)

def current_user(ctx) -> User:
    username = ctx["user"].get("name")
    email = ctx["user"].get("preferred_username")

    user = User.query.filter_by(username=username).first()

    if not user:
        new_user = User(username=username, email=email)
        db.session.add(new_user)
        db.session.commit()

        user = new_user

    return user

FREE_CLASSROOMS_CSV = 'ucilnice.csv'
TESTS_DIR = 'static/tests' # Stari testi
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'} # Allowed extension for image upload

def sendEmail(subject: str = '', recipients: list[str] | None = None, content: str = '', heading: str = ''):
    """
    Send email from the 'tutorstvo@kladnik.cc' email address
    """

    if recipients:
        recipients = list(filter(None, recipients)) # Remove empty recipients

    else:
        recipients = []

    if recipients:
        msg = Message(
            subject=f'[Tutorstvo]: {subject}',
            sender='tutorstvo@kladnik.cc',
            recipients=recipients,
            html=render_template('email.html', content=content, title=heading)
        )

        try:
            mail.send(msg)

            return ''
        except Exception as e:
            return f'Error whilst sending email: {e}'

def getEmails(usernames: list[str]) -> list[str]:
    """
    Get email addresses for multiple users
    """

    emails = []
    for username in usernames:
        emails.append(User.query.filter_by(username=username).first().email)

    return emails

def isAllowedFile(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

        if current_user(context).is_admin():
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

        if current_user(context).is_admin() or current_user(context).is_tutor(Subject):
            return func(*args, context=context, **kwargs)

        flash("You must be a tutor (or higher) to access this page.", "danger")
        return redirect(url_for('views.home'))

    return wrapper

def login_required(func):
    """
    Rename auth.login_required to login_required
    """

    return auth.login_required(func)

@views.route('/')
@login_required
def index(*, context):
    return redirect(url_for('views.home'))

@views.route('/toggle-dark-mode')
@login_required
def toggleDarkMode(*, context):
    current_user(context).dark_mode = not current_user(context).dark_mode
    db.session.commit()

    return redirect(request.referrer)

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
            user = User.query.filter_by(username=current_user(context).username).first()
            user.role = 'admin'
            db.session.commit()

            print(f"Made '{current_user(context).username}' admin.")
            return redirect(url_for('views.home'))
        else:
            flash("Wrong password", "danger")

    return render_template("admin.html", current_user=current_user(context), form=form)

@views.route('/admin-panel')
@login_required
@admin_required
def adminPanel(*, context):
    admins = User.query.filter_by(role="admin").all()
    tutors = [user for user in User.query.all() if user.tutor_for(Subject) != []]
    subjects = Subject.query.all()
    groups = [group.name for group in Group.query.all()]
    group_ids = [group.id for group in Group.query.all()]
    users = User.query.all()

    return render_template("admin_panel.html", current_user=current_user(context), admins=admins, users=users, tutors=zip(list(map(lambda tutor: tutor.tutor_for(Subject), tutors)), tutors), subjects=subjects, subject_names=[s.name for s in subjects], groups=groups, group_ids=group_ids, formatTitle=formatTitle, zip=zip, set=set, list=list)

@views.route('/remove-user/<id>')
@login_required
@admin_required
def remove_user(*, context, id):
    user = User.query.filter_by(id=id).first()
    db.session.delete(user)

    db.session.commit()

    return redirect(request.referrer)

@views.route('/add-subject', methods=['GET', 'POST'])
@login_required
@admin_required
def addSubject(*, context):
    if request.form:
        name = request.form['name']

        if not Subject.query.filter_by(name=name).first():
            new_subject = Subject(name=name, tutors='')
            db.session.add(new_subject)

            db.session.commit()

    return redirect(request.referrer)

@views.route('/remove-subject/<name>')
@login_required
@admin_required
def removeSubject(*, context, name):
    subject = Subject.query.filter_by(name=name).first()
    db.session.delete(subject)

    db.session.commit()

    return redirect(request.referrer)

@views.route('/add-group', methods=['POST'])
@login_required
@admin_required
def addGroup(*, context):
    if request.form:
        name = request.form['name']

        try:
            new_group = Group(name=name)
            db.session.add(new_group)

            db.session.commit()
        except:
            pass

    return redirect(request.referrer)

@views.route('/remove-group/<id>')
@login_required
@admin_required
def removeGroup(*, context, id):
    group = Group.query.filter_by(id=id).first()
    db.session.delete(group)

    db.session.commit()

    return redirect(request.referrer)

@views.route('/add-to-group',  methods=['POST'])
@login_required
@admin_required
def addToGroup(*, context):
    if request.form:
        groups = request.form.getlist('groups[]')
        username = request.form['username']

        user = User.query.filter_by(username=username).first()
        user.groups = ','.join(groups)

        db.session.commit()

    return redirect(request.referrer)

@views.route('/add-role/<role>', methods=['POST'])
@login_required
@admin_required
def addRole(*, context, role):
    if request.form:
        username = request.form['username']

        user = User.query.filter_by(username=username).first()

        if user:
            if role == 'admin':
                user.role = role

            elif role == 'tutor':
                subjects = list(set(request.form.getlist('subjects[]')))

                for subject in subjects:
                    s = Subject.query.filter_by(name=subject).first()

                    if not (user.username in s.get_tutors()):
                        s.tutors = ','.join(s.get_tutors() + [user.username])

            print(f"Gave role {role} to '{user.username}'.")

            db.session.commit()

        else:
            flash('There is no user with that name.', 'danger')

    return redirect(request.referrer)

@views.route('/remove-role/<role>/<int:id>')
@login_required
@admin_required
def removeRole(*, context, role, id):
    user = User.query.filter_by(id=id).first()

    if role == 'admin':
        user.role = 'user'

    elif role == 'tutor':
        if user.role != 'admin':
            user.role = 'user'


        subjects = Subject.query.filter_by().all()

        for s in subjects:
            if user.username in s.get_tutors():
                s.tutors = ','.join(set(s.get_tutors()) - {user.username})

    db.session.commit()

    return redirect(request.referrer)

@views.route('/home')
@login_required
def home(*, context):
    lessons = Lesson.query.filter(Lesson.id.in_(current_user(context).getSelectedSubjects()))

    return render_template('index.html', current_user=current_user(context), lessons=lessons, subject_db=Subject)

months = {
    1: 'januar',
    2: 'februar',
    3: 'marec',
    4: 'april',
    5: 'maj',
    6: 'junij',
    7: 'julij',
    8: 'avgust',
    9: 'september',
    10: 'oktober',
    11: 'november',
    12: 'december'
}

days = {
    0: 'Ponedeljek',
    1: 'Torek',
    2: 'Sreda',
    3: 'Četrtek',
    4: 'Petek',
    5: 'Sobota',
    6: 'Nedelja'
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
    for lesson in Lesson.query.all():
        if datetime.strptime(lesson.datetime.split(' ')[0], DATETIME_FORMAT_JS) < datetime.today() - timedelta(days=1):
            db.session.delete(lesson)

        db.session.commit()

    if request.form and (current_user(context).is_tutor(Subject) or current_user(context).is_admin()):
        form = request.form

        new_lesson = Lesson(groups=form['group'], subject=form['title'], classroom=form['classroom'], min=form['min'], max=form['max'], datetime=form['datetime'] or f"{datetime.now().year}/{datetime.now().day}/{datetime.now().month} 00:00", description=form['description'])
        db.session.add(new_lesson)

        db.session.commit()

    search = request.args.get('search', None)

    lessons = Lesson.query.filter(Lesson.id.notin_(current_user(context).getSelectedSubjects()))
    mask = list(map(lambda lesson: any(map(lambda x: x in current_user(context).get_groups(), lesson.get_groups())), lessons))
    lessons = [d for d, m in zip(lessons, mask) if m]

    side = [('PRE', '7:10', '7:55'), ('O', '10:25', '10:55'), ('6', '12:40', '13:25'), ('7', '13:30', '14:15'), ('8', '14:20', '15:05')]

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

    free_classrooms = []
    with open(FREE_CLASSROOMS_CSV, "r") as f:
        reader = csv.reader(f)
        for i in list(reader):
            free_classrooms.append([i[0], i[1], i[2], i[3].split(',')])

    free_classrooms = str(free_classrooms).replace("'", '"')

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

    return render_template('tutorstvo.html', current_user=current_user(context), mobile=mobile, search=search, lessons=lessons, subjects=subjects, all_subjects=all_subjects, subject_db=Subject, days=days_, startNext=startNext, rows=rows, enumerate=enumerate, free_classrooms=free_classrooms, len=len, str=str)

@views.route('/tutorstvo/add/<int:id>')
@login_required
def selectLesson(*, context, id):
    lesson = Lesson.query.filter_by(id=id).first()

    if not (current_user(context).username in lesson.get_tutors(Subject)) and not (lesson.filled >= lesson.max):
        current_user(context).selected_subjects = ','.join(set(current_user(context).getSelectedSubjects() + [str(id)]))

        lesson.filled += 1

        if lesson.filled == lesson.min:
            addr = list(filter(None, getEmails(lesson.get_tutors(Subject))))

            if addr:
                sendEmail(f'{lesson.subject}', addr, f"""Pozdravljeni,

        Za predmet {lesson.subject} je število učencev preseglo minimalno mejo. To pomeni da se bo ura odvijala.""", f'Tutorstvo - {lesson.subject}')

        db.session.commit()

        return redirect(url_for('views.home'))

    return redirect(request.referrer)

@views.route('/tutorstvo/remove/<int:id>')
@login_required
def deselectLesson(*, context, id):
    lesson = Lesson.query.filter_by(id=id).first()
    selected = current_user(context).getSelectedSubjects()

    if lesson:
        current_user(context).selected_subjects = ','.join(set(selected) - set(str(id)))

        lesson.filled -= 1

        if lesson.filled == lesson.min - 1:
            addr = list(filter(None, getEmails(lesson.get_tutors(Subject))))

            if addr:
                sendEmail(f'{lesson.subject}', addr, f"""Pozdravljeni,

        Za predmet {lesson.subject} je število učencev spet padlo pod minimalno mejo. To pomeni da se ura ne bo odvijala.""", f'Tutorstvo - {lesson.subject}')

        db.session.commit()

        return redirect(url_for('views.home'))

    return redirect(request.referrer)

@views.route('/remove-lesson/<int:id>')
@login_required
@tutor_required
def removeLesson(*, context, id):
    lesson = Lesson.query.filter_by(id=id).first()
    subjects = current_user(context).subjects(Subject)

    if lesson.subject.lower() in subjects:
        db.session.delete(lesson)

        db.session.commit()

    else:
        print(f'{current_user(context).username} tried to delete without permissions.')

    return redirect(request.referrer)

@views.route('/learning-resources')
@login_required
def learning_resources(*, context):
    subjects = Subject.query.all()

    return render_template('learning_resources.html', current_user=current_user(context), subjects=subjects)

@views.route('/add-learning-resource', methods=['POST'])
@login_required
@admin_required
def add_learning_resource(*, context):
    if request.form:
        subject_name = request.form['subject']
        url = request.form['url']

        subject = Subject.query.filter_by(name=subject_name).first()
        subject.learning_resources = ','.join(set(subject.get_learning_resources() + [url]))  

        db.session.commit()

    return redirect(request.referrer)

@views.route('/remove-learning-resource')
@login_required
@admin_required
def remove_learning_resource(*, context):
    url = request.args.get('url', None)
    subject_name = request.args.get('subject', None)

    if (url and subject_name):
        subject = Subject.query.filter_by(name=subject_name).first()
        subject.learning_resources = ','.join(set(subject.get_learning_resources()) - set([url]))

        db.session.commit()

    return redirect(request.referrer)

