from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm, AdminForm, ChangePasswordForm
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, login_required, logout_user, current_user
from extensions import login_manager
from extensions import db, mail, cache
from flask_mail import Message
from functools import wraps
from models import User, Subject, Lesson, Group
from resources import formatTitle, confirm_token, generate_confirmation_token, secrets
import os
from datetime import datetime, timedelta

views = Blueprint('views', __name__)

TESTS_DIR = 'static/tests' # Stari testi
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'} # Allowed extension for image upload

def sendEmail(subject: str = '', recipients: list[str] | None = None, content: str = '', heading: str = ''):
    """
    Send email from the 'tutorstvo@kladnik.cc' email address
    """

    recipients = list(filter(None, recipients)) # Remove empty recipients

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
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for('views.home'))

        if current_user.is_admin():
            return func(*args, **kwargs)

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
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for('views.home'))

        if current_user.is_admin() or current_user.is_tutor():
            return func(*args, **kwargs)

        flash("You must be a tutor (or higher) to access this page.", "danger")
        return redirect(url_for('views.home'))

    return wrapper

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=int(user_id)).first()

@views.route('/')
def index():
    return redirect(url_for('views.login'))

@views.route('/toggle-dark-mode')
def toggleDarkMode():
    current_user.dark_mode = not current_user.dark_mode
    db.session.commit()

    return redirect(request.referrer)

@views.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)

            return redirect(url_for('views.home'))
        else:
            flash("Invalid username or password", "danger")
            form.username.data = ''

    return render_template("login.html", form=form)

@views.route("/logout")
@login_required
def logout():
    logout_user()

    return redirect(url_for('views.login'))

@views.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data != form.password_confirm.data:
            flash('Gesli se ne ujemata', 'danger')
            return redirect(url_for('views.register'))

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data.lower(), password=hashed_password)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError as e:
            flash("A user with that name already exists.", "danger")
            form.username.data = ''
            return render_template("register.html", form=form)
        
        return redirect(url_for('views.login'))
    
    return render_template("register.html", form=form)

@views.route('/change-password', methods=['GET', 'POST'])
@login_required
def changePassword():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not check_password_hash(current_user.password, form.prev_password.data):
            flash('Trenutno geslo ni pravilno.', 'danger')
            return redirect(url_for('views.change_password'))

        if form.new_password.data != form.password_confirm.data:
            flash('Gesli se ne ujemata', 'danger')
            return redirect(url_for('views.change_password'))

        hashed_password = generate_password_hash(form.new_password.data)
        current_user.password=hashed_password
        
        db.session.commit()
        
        logout_user()
        
        return redirect(url_for('views.login'))
    
    return render_template("change_password.html", form=form)

@views.route('/admin', methods=['GET', 'POST'])
@login_required
def requestAdmin():
    form = AdminForm()
    if form.validate_on_submit():
        hash = secrets['admin-password']

        if check_password_hash(hash, form.password.data):
            user = User.query.filter_by(username=current_user.username).first()
            user.role = 'admin'
            db.session.commit()

            print(f"Made '{current_user.username}' admin.")
            return redirect(url_for('views.home'))
        else:
            flash("Wrong password", "danger")

    return render_template("admin.html", form=form)

@views.route('/admin-panel')
@admin_required
def adminPanel():
    admins = User.query.filter_by(role="admin").all()
    tutors = [user for user in User.query.all() if user.tutor_for(Subject) != []]
    subjects = Subject.query.all()
    groups = [group.name for group in Group.query.all()]
    group_ids = [group.id for group in Group.query.all()]
    users = User.query.all()

    return render_template("admin_panel.html", admins=admins, users=users, tutors=zip(list(map(lambda tutor: tutor.tutor_for(Subject), tutors)), tutors), subjects=subjects, groups=groups, group_ids=group_ids, formatTitle=formatTitle, zip=zip, set=set, list=list)

@views.route('/add-subject', methods=['GET', 'POST'])
@admin_required
def addSubject():
    if request.form:
        name = request.form['name'].lower()
        
        if not Subject.query.filter_by(name=name).first():
            new_subject = Subject(name=name, tutors='')
            db.session.add(new_subject)

            db.session.commit()

    return redirect(request.referrer)

@views.route('/remove-subject/<name>')
@admin_required
def removeSubject(name):
    subject = Subject.query.filter_by(name=name).first()
    db.session.delete(subject)

    db.session.commit()

    return redirect(request.referrer)

@views.route('/add-group', methods=['POST'])
@admin_required
def addGroup():
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
@admin_required
def removeGroup(id):
    group = Group.query.filter_by(id=id).first()
    db.session.delete(group)

    db.session.commit()

    return redirect(request.referrer)

@views.route('/add-to-group',  methods=['POST'])
@admin_required
def addToGroup():
    if request.form:
        groups = request.form.getlist('groups[]')
        username = request.form['username']

        user = User.query.filter_by(username=username.lower()).first()
        user.groups = ','.join(groups)

        db.session.commit()

    return redirect(request.referrer)

@views.route('/add-role/<role>', methods=['POST'])
@admin_required
def addRole(role):
    if request.form:
        username = request.form['username'].lower()

        user = User.query.filter_by(username=username).first()

        if user:
            if role == 'admin':
                user.role = role
                

            elif role == 'tutor':
                subjects = list(set(request.form.getlist('subjects[]')))

                for subject in subjects:
                    s = Subject.query.filter_by(name=subject).first()

                    if not (user.username.lower() in s.get_tutors()):
                        s.tutors = ','.join(s.get_tutors() + [user.username])

            print(f"Gave role {role} to '{user.username}'.")

            db.session.commit()
        
        else:
            flash('There is no user with that name.', 'danger')
        
    return redirect(request.referrer)

@views.route('/remove-role/<role>/<int:id>')
@admin_required
def removeRole(role, id):
    user = User.query.filter_by(id=id).first()

    if role == 'admin':
        user.role = 'user'

    elif role == 'tutor':
        if user.role != 'admin':
            user.role = 'user'


        subjects = Subject.query.filter_by().all()

        for s in subjects:
            if user.username.lower() in s.get_tutors():
                s.tutors = ','.join(set(s.get_tutors()) - {user.username})

    db.session.commit()

    return redirect(request.referrer)

@views.route('/home')
@login_required
def home():
    lessons = Lesson.query.filter(Lesson.id.in_(current_user.getSelectedSubjects()))

    return render_template('index.html', lessons=lessons, subject_db=Subject)

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
def tutorstvo():
    if request.form and (current_user.is_tutor() or current_user.is_admin()):
        form = request.form

        new_lesson = Lesson(groups=form['group'], subject=form['title'], classroom=form['classroom'], min=form['cap'], datetime=form['datetime'] or f"{datetime.now().year}/{datetime.now().day}/{datetime.now().month} 00:00", description=form['description'])
        db.session.add(new_lesson)

        db.session.commit()

    lessons = Lesson.query.filter(Lesson.id.notin_(current_user.getSelectedSubjects()))
    mask = list(map(lambda lesson: any(map(lambda x: x in current_user.get_groups(), lesson.get_groups())), lessons))
    lessons = [d for d, m in zip(lessons, mask) if m]
    
    side = [('PRE', '7:10', '7:55'), ('O', '10:25', '10:55'), ('6', '12:40', '13:25'), ('7', '13:30', '14:15'), ('8', '14:20', '15:05')] 
    
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile = False
    if any(mobile in user_agent for mobile in ['iphone', 'android', 'ipad', 'mobile']):
        mobile = True

    startDate = request.args.get('date')
    if startDate and not mobile:
        startDate = datetime.strptime(startDate, '%d-%m-%Y')
        startDate = startDate - timedelta(days=startDate.weekday())

    elif not mobile:
        startDate = datetime.today() - timedelta(days=datetime.today().weekday())

    elif not startDate:
        startDate = datetime.today()

    else:
        startDate = datetime.strptime(startDate, '%d-%m-%Y')

    lessons_by_column = []
    lesson_dates = []

    r = 1 if mobile else 5
    for i in range(r):
        column = []
        column_lessons = list(filter(lambda lesson: lesson.datetime.split(' ')[0] == (startDate + timedelta(days=i)).strftime("%Y/%d/%m"), lessons))
        
        for j in side:
            lesson_date = f'{(startDate + timedelta(days=i)).strftime("%Y/%d/%m")} {j[1]}'

            for lesson in column_lessons:
                if isInTimeRange(lesson.datetime.split(' ')[1], (j[1], j[2])):
                    column.append((lesson_date, lesson))

                else:
                    column.append((lesson_date, ''))


            if not column_lessons:
                column.append((lesson_date, ''))

        lessons_by_column.append(column)

    lessons_by_row = [list(x) for x in zip(*lessons_by_column)]

    startNext = [(startDate - timedelta(days=7)).strftime('%d-%m-%Y'), (startDate + timedelta(days=7)).strftime('%d-%m-%Y')]
    subjects = current_user.subjects(Subject)

    days_ = getWeek(startDate)
    rows = (lessons_by_row, side)

    if mobile:
        days_ = [(days[startDate.weekday()], f"{startDate.day}. {months[startDate.month]}"), days[startDate.weekday()]]
        startNext = [(startDate - timedelta(days=1)).strftime('%d-%m-%Y'), (startDate + timedelta(days=1)).strftime('%d-%m-%Y')]

    return render_template('tutorstvo.html', mobile=mobile, lessons=lessons, subjects=subjects, subject_db=Subject, days=days_, startNext=startNext, rows=rows, enumerate=enumerate)

@views.route('/tutorstvo/add/<int:id>')
def selectLesson(id):
    lesson = Lesson.query.filter_by(id=id).first()
    
    if not (current_user.username.lower() in lesson.get_tutors(Subject)):
        current_user.selected_subjects = ','.join(set(current_user.getSelectedSubjects() + [str(id)]))

        lesson.filled += 1

        if lesson.filled == lesson.min:
            addr = list(filter(None, getEmails(lesson.get_tutors(Subject))))

            if addr:
                sendEmail(f'{lesson.subject}', addr, f"""Pozdravljeni,

        Za predmet {lesson.subject} je število učencev preseglo minimalno mejo. To pomeni da se bo ura odvijala.""", f'Tutorstvo - {lesson.subject}')

        db.session.commit()

        return redirect(url_for('views.home'))
    
    return redirect(url_for('views.tutorstvo'))

@views.route('/tutorstvo/remove/<int:id>')
def deselectLesson(id):
    lesson = Lesson.query.filter_by(id=id).first()
    selected = current_user.getSelectedSubjects()

    if lesson:
        current_user.selected_subjects = ','.join(set(selected) - set(str(id)))

        lesson.filled -= 1

        if lesson.filled == lesson.min - 1:
            addr = filter(None, getEmails(lesson.get_tutors(Subject)))

            if addr:
                sendEmail(f'{lesson.subject}', addr, f"""Pozdravljeni,

        Za predmet {lesson.subject} je število učencev spet padlo pod minimalno mejo. To pomeni da se ura ne bo odvijala.""", f'Tutorstvo - {lesson.subject}')

        db.session.commit()

        return redirect(url_for('views.home'))
    
    return redirect(url_for('views.tutorstvo'))

@views.route('/remove-lesson/<int:id>')
@tutor_required
def removeLesson(id):
    lesson = Lesson.query.filter_by(id=id).first()
    subjects = current_user.subjects(Subject)

    if lesson.subject.lower() in subjects:
        db.session.delete(lesson)

        db.session.commit()

    else:
        print(f'{current_user.username} tried to delete without permissions.')

    return redirect(url_for('views.tutorstvo'))

# @views.route('/tests')
@login_required
def tests():
    if not os.path.exists(TESTS_DIR):
       os.makedirs(TESTS_DIR)

    return render_template('tests.html', images=os.listdir(TESTS_DIR), tests_dir=TESTS_DIR)

# @views.route('/add-test-im', methods=['POST'])
@admin_required
def addTestImage():
    file = request.files['file']
    directory = TESTS_DIR
    subject = request.form['subject'].lower()
    n = request.form['number']
    ch = 97

    if file and isAllowedFile(file.filename):
        if not os.path.exists(directory):
            os.makedirs(directory)

        for i in os.listdir(directory):
            if i.startswith(subject):
                ch += 1

        filename = os.path.join(directory, f'{subject}_{n}{chr(ch)}.{file.filename.rsplit(".", 1)[1]}')

        file.save(filename)
            
    return redirect(request.referrer)

# @views.route('/remove-test-im/<path>')
@cache.cached(timeout=60)
@admin_required
def removeTestImage(path):
    path = os.path.join(TESTS_DIR, path)

    if os.path.exists(path):
        os.remove(path)

    return redirect(request.referrer)


@views.route('/account')
@login_required
def account():
    return render_template('account.html', email=current_user.email if current_user.email else 'Email naslov ni nastavljen', formatTitle=formatTitle)

@views.route('/send-email/register', methods=['POST'])
@login_required
def registerEmail():
    if request.form:
        email = request.form['email']

        if current_user.email == email:
            return redirect(request.referrer)

        current_user.unverified_email = email

        db.session.commit()

        token = generate_confirmation_token(email)

        confirm_url = url_for("views.confirm_email", token=token, _external=True) 
        
        content = f"""<p>Dober dan {formatTitle(current_user.username)},</p>
        
        <p>Da dokončate registracijo email naslova kliknite na spodnji gumb.</p>
        <p class="button-container">
            <a href="{confirm_url}" class="button">Potrdite Email naslov</a>
        </p>
        <p>Če se niste prijavili v ta račun, lahko to sporočilo mirno prezrete.</p>"""

        r = sendEmail(subject="Potrditev email naslova", recipients=[email], content=content, heading='Potrditev email naslova')
        
        if r:
            print(r)

    return redirect(request.referrer)

@views.route("/confirm-email/<token>")
def confirmEmail(token):
    email = confirm_token(token)
    
    if not email:
        flash("Invalid or expired token", "danger")
        return redirect(url_for("views.login"))

    user = User.query.filter_by(unverified_email=email).first_or_404()
    user.email = email

    db.session.commit()  

    return redirect(url_for("views.account"))

@views.route('/learning-resources')
@login_required
def learning_resources():
    subjects = Subject.query.all()

    return render_template('learning_resources.html', subjects=subjects)

@views.route('/add-learning-resource', methods=['POST'])
@admin_required
def add_learning_resource():
    if request.form:
        subject_name = request.form['subject']
        url = request.form['url']

        subject = Subject.query.filter_by(name=subject_name).first()
        subject.learning_resources = ','.join(set(subject.get_learning_resources() + [url]))  

        db.session.commit()

    return redirect(request.referrer)

@views.route('/remove-learning-resource')
@admin_required
def remove_learning_resource():
    url = request.args.get('url', None)
    subject_name = request.args.get('subject', None)

    if (url and subject_name):
        subject = Subject.query.filter_by(name=subject_name).first()
        subject.learning_resources = ','.join(set(subject.get_learning_resources()) - set([url]))

        db.session.commit()

    return redirect(request.referrer)

