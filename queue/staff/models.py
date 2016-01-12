"""
Important: Changes here need to be followed by `make refresh`.
"""

from queue import db
from sqlalchemy import types
from sqlalchemy_utils import EncryptedType, PasswordType
from sqlalchemy_utils.types.choice import ChoiceType

#############
# UTILITIES #
#############

def add_obj(obj):
    """
    Add object to database

    :param obj: any instance of a Model
    :return: information regarding database add
    """
    db.session.add(obj)
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
    created_at = db.Column(db.DateTime)


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
        ('resolved', 'addressed and closed'),
        ('closed', 'closed without resolution - end of session, MIA etc.')
    )

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(ChoiceType(STATUSES), default='unresolved')
    name = db.Column(db.String(50))
    question = db.Column(db.Text)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    resolvers = db.relationship('User', secondary=resolutions,
        backref=db.backref('resolutions', lazy='dynamic'))
    category = db.Column(ChoiceType(CATEGORIES))
    created_at = db.Column(db.DateTime)

    @property
    def assignment(self):
        return Assignment.query.filter_by(id=self.assignment_id).first()

    @property
    def problem(self):
        return Problem.query.filter_by(id=self.problem_id).first()

    @property
    def owner(self):
        return Owner.query.filter_by(id=self.owner_id).first()


class Assignment(db.Model):
    """Assignments"""

    __tablename__ = 'assignment'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    inquiries = db.relationship('Inquiry', backref='assignment', lazy='dynamic')
    problems = db.relationship('Problem', backref='assignment', lazy='dynamic')
    created_at = db.Column(db.DateTime)


class Problem(db.Model):
    """Problems in assignment"""

    __tablename__ = 'problem'

    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(10))
    description = db.Column(db.Text)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))
    created_at = db.Column(db.DateTime)
