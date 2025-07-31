from extensions import db
from resources import formatTitle, get_leaderboard

class Subject(db.Model):
    __bind_key__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    tutors = db.Column(db.String(100), nullable=False)
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

    def get_groups(self) -> list:
        groups_str = self.groups

        return groups_str.split(',')

    def get_year(self) -> str:
        r = list(filter(lambda g: g in ["y1", "y2", "y3", "y4"], self.get_groups()))

        return r[0] if r else ''

    def is_admin(self):
        return self.role == 'admin'

    def is_tutor(self, subject_db):
        for subject in subject_db.query.all():
            for i in subject.get_tutors():
                if i == self.username:
                    return True

        return False

    def tutor_for(self, subject_db):
        subjects = []
        for subject in subject_db.query.all():
            for i in subject.get_tutors():
                if i == self.username:
                    subjects.append(subject.name)

        return subjects

    def is_tutor_for(self, subject):
        return self.username in subject.get_tutors()

    def subjects(self, subject_db):
        subjects = []

        if self.is_admin():
            subjects = list(map(lambda x: x.name, subject_db.query.all()))

        elif self.is_tutor(subject_db):
            for subject in subject_db.query.all():
                for i in subject.get_tutors():
                    if i == self.username:
                        subjects.append(subject.name)

        return subjects

    def getSelectedSubjects(self):
        return list((filter(None, self.selected_subjects.split(','))))

    def getLeaderBoardPos(self, subject_db):
        if not self.is_tutor(subject_db):
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

    def get_groups(self) -> list:
        groups_str = self.groups

        return groups_str.split(',')

    def isInGroup(self, group: str) -> bool:
        return group in self.get_groups()

    def get_tutors(self, subject_db: Subject, user_db: User) -> list:
        for_subj = subject_db.query.filter_by(name=self.subject).first().get_tutors()

        tutors = []
        for username in for_subj:
            user = user_db.query.filter_by(username=username).first()
            if not user:
                continue

            for group in user.get_groups():
                if self.isInGroup(group):
                    tutors.append(user.username)
                    break

        return tutors

    def tutors(self, subject_db: Subject, user_db: User) -> str:
        return ', '.join(list(map(formatTitle, self.get_tutors(subject_db, user_db))))

class Group(db.Model):
    __bind_key__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
