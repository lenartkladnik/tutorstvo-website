from extensions import db
from resources import get_leaderboard, DATETIME_FORMAT_PY, DATETIME_FORMAT_USER, is_lesson_removable, ALLOWED_GROUPS, HUMAN_READABLE_GROUPS
from datetime import datetime, timedelta

class Subject(db.Model):
    __bind_key__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    tutors = db.Column(db.String(1000), nullable=False)
    learning_resources = db.Column(db.String(1000), default='', nullable=False)

    def get_tutors(self) -> list:
        return list(filter(None, self.tutors.split(',')))

    def get_learning_resources(self) -> list:
        return list(filter(None, self.learning_resources.split(',')))

class User(db.Model):
    __bind_key__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    groups = db.Column(db.String(200), default='', nullable=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50), default='user')
    selected_subjects = db.Column(db.String(200), default='', nullable=False)
    email = db.Column(db.String(100), default='', nullable=False)
    dark_mode = db.Column(db.Boolean, default=False, nullable=False)
    score = db.Column(db.Integer, default=0)
    applied_subjects = db.Column(db.String(200), default='', nullable=False)
    rejected = db.Column(db.Integer, default=0)
    rejected_at = db.Column(db.String)
    tutoring_subjects = db.Column(db.String(200), default='', nullable=False)
    issues = db.Column(db.Integer, default=0)

    def is_rejected(self) -> bool:
        return self.rejected == 1

    def reject(self):
        self.rejected = 1
        self.rejected_at = datetime.now().strftime(DATETIME_FORMAT_PY)

    def accept(self):
        self.rejected = -1
        self.rejected_at = None
        self.issues = 0

    def rejection_expires_at(self) -> datetime | None:
        if not self.rejected_at:
            return None

        return datetime.strptime(self.rejected_at, DATETIME_FORMAT_PY) + timedelta(weeks=4)

    def rejection_expires_at_str(self) -> str:
        exp = self.rejection_expires_at()
        if not exp:
            return ''

        return datetime.strftime(exp, DATETIME_FORMAT_USER)

    def rejection_expired(self) -> bool:
        exp = self.rejection_expires_at()
        if not exp:
            return True

        if datetime.now() > exp:
            return True

        return False

    def get_applied_subjects(self) -> list:
        return self.applied_subjects.split(', ')

    def get_tutoring_subjects(self) -> list:
        return self.tutoring_subjects.split(',')

    def get_groups(self) -> list:
        groups_str = self.groups

        return groups_str.split(',')

    def get_year(self) -> str:
        r = list(filter(lambda g: g in ALLOWED_GROUPS, self.get_groups()))

        return r[0] if r else ''

    def tutoring_years(self) -> list[str]:
        years = []

        for y in ALLOWED_GROUPS:
            years.append(y)
            if self.get_year() == y:
                break

        return years

    def is_admin(self):
        return self.role == 'admin'

    def is_tutor(self):
        return self.tutor_for() != []

    def tutor_for(self):
        return list(filter(None, map(str.lower, self.get_tutoring_subjects())))

    def is_tutor_for(self, subject):
        return subject.name.lower() in self.tutor_for()

    def subjects(self, subject_db):
        subjects = []

        if self.is_admin():
            subjects = list(map(lambda x: x.name, subject_db.query.all()))

        elif self.is_tutor():
            for subject in subject_db.query.all():
                for i in subject.get_tutors():
                    if i == self.username:
                        subjects.append(subject.name)

        return subjects

    def getSelectedSubjects(self):
        return list((filter(None, self.selected_subjects.split(','))))

    def getSelectedSubjectsInt(self):
        return list(map(int, self.getSelectedSubjects()))

    def getLeaderBoardPos(self):
        if not self.is_tutor():
            return None

        lb = get_leaderboard(self, Subject)
        for i in lb:
            if i[0] == self.username:
                return i[1]

class Lesson(db.Model):
    __bind_key__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)
    groups = db.Column(db.String(200), default='', nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    classroom = db.Column(db.String(10), nullable=False)
    min = db.Column(db.Integer)
    max = db.Column(db.Integer)
    datetime = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    filled = db.Column(db.Integer, default=0)
    tutors = db.Column(db.String(1000), default='', nullable=False)
    passed = db.Column(db.Integer, default=-1)

    def has_passed(self) -> bool:
        return self.passed == 1

    def is_removable(self) -> bool:
        return is_lesson_removable(self)

    def set_passed(self):
        self.passed = 1

    def get_groups(self) -> list:
        groups_str = self.groups

        return groups_str.split(',')

    def human_readable_groups(self) -> str:
        # return ', '.join([HUMAN_READABLE_GROUPS[i] for i in self.get_groups()])

        string_list = []

        for y in self.get_groups():
            string_list.append(y[1] + '.')

        string = ', '.join(string_list)
        string += ' letnik'

        return string

    def isInGroup(self, group: str) -> bool:
        return group in self.get_groups()

    def get_tutors(self) -> list:
        return list(filter(None, self.tutors.split(', ')))

    def get_users(self, user_db) -> list:
        users = []
        for user in user_db.query.filter_by():
            if self in Lesson.query.filter(Lesson.id.in_(user.getSelectedSubjects())):
                users.append(user)

        return users

class Group(db.Model):
    __bind_key__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
