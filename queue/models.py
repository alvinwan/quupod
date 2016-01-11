from . import db
from sqlalchemy import types
from sqlalchemy_utils.types.choice import ChoiceType


resolutions = db.Table('resolutions',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('request_id', db.Integer, db.ForeignKey('request.id')),
    db.Column('comment', db.Text)
)


class User(db.Model):
    """queue system user"""

    ROLES = (
        ('student', 'student'),
        ('staff', 'reader, tutor, GSI, or professor'))

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(ChoiceType(ROLES))
    requests = db.relationship('Request', backref='user', lazy='dynamic')


class Request(db.Model):
    """request placed in queue"""

    STATUSES = (
        ('unresolved', 'has not yet been addressed'),
        ('resolving', 'being addressed by staff'),
        ('resolved', 'addressed and closed')

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(ChoiceType(STATUSES))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    resolvers = db.relationship('User', secondary=resolutions,
        backref=db.backref('resolutions', lazy='dynamic'))
