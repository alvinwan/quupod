from queue import db
from sqlalchemy import types
from sqlalchemy_utils import EncryptedType, PasswordType
from sqlalchemy_utils.types.choice import ChoiceType

#############
# UTILITIES #
#############

def save(self):
    db.session.add(self)
    db.session.commit()

##########
# MODELS #
##########

resolutions = db.Table('resolutions',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('inquiry_id', db.Integer, db.ForeignKey('inquiry.id')),
    db.Column('comment', db.Text)
)


class User(db.Model):
    """queue system user"""

    __tablename__ = 'user'

    ROLES = (
        ('student', 'student'),
        ('staff', 'reader, tutor, GSI, or professor')
    )

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(ChoiceType(ROLES))
    inquiries = db.relationship('Inquiry', backref='owner', lazy='dynamic')
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True)
    password = db.Column(PasswordType(schemes=['pbkdf2_sha512']))


class Inquiry(db.Model):
    """inquiry placed in queue"""

    __tablename__ = 'inquiry'

    CATEGORIES = (
        ('question', 'question'),
        ('tutoring', 'tutoring')
    )

    STATUSES = (
        ('unresolved', 'has not yet been addressed'),
        ('resolving', 'being addressed by staff'),
        ('resolved', 'addressed and closed')
    )

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(ChoiceType(STATUSES))
    name = db.Column(db.String(50))
    question = db.Column(db.Text)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    resolvers = db.relationship('User', secondary=resolutions,
        backref=db.backref('resolutions', lazy='dynamic'))
    category = db.Column(ChoiceType(CATEGORIES))


class Assignment(db.Model):
    """Assignments"""

    __tablename__ = 'assignment'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    inquiries = db.relationship('Inquiry', backref='assignment', lazy='dynamic')
    problems = db.relationship('Problem', backref='assignment', lazy='dynamic')


class Problem(db.Model):
    """Problems in assignment"""

    __tablename__ = 'problem'

    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(10))
    description = db.Column(db.Text)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))