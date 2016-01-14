"""
Important: Changes here need to be followed by `make refresh`.
"""

from queue import db
from sqlalchemy import types
from sqlalchemy_utils import EncryptedType, PasswordType, ArrowType
from sqlalchemy_utils.types.choice import ChoiceType
import flask_login, arrow

##########
# MODELS #
##########


class Resolution(db.Model):

    __tablename__ = 'resolution'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(ArrowType, default=arrow.utcnow())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    inquiry_id = db.Column(db.Integer, db.ForeignKey('inquiry.id'))
    resolved_at = db.Column(ArrowType)
    comment = db.Column(db.Text)

    @property
    def inquiry(self):
        return Inquiry.query.filter_by(id=self.inquiry_id).first()


class User(db.Model, flask_login.UserMixin):
    """queue system user"""

    __tablename__ = 'user'

    ROLES = (
        ('student', 'student'),
        ('staff', 'reader, tutor, GSI, or professor')
    )

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(ArrowType, default=arrow.utcnow())

    role = db.Column(ChoiceType(ROLES), default='student')
    inquiries = db.relationship('Inquiry', backref='owner', lazy='dynamic')
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True)
    password = db.Column(PasswordType(schemes=['pbkdf2_sha512']))
    created_at = db.Column(ArrowType, default=arrow.utcnow())


class Inquiry(db.Model):
    """inquiry placed in queue"""

    __tablename__ = 'inquiry'

    CATEGORIES = (
        ('question', 'question'),
        ('tutoring', 'tutoring')
    )

    STATUSES = (
        ('unresolved', 'has not yet been addressed'),
        ('resolving', 'being addressed by admin'),
        ('resolved', 'addressed and closed'),
        ('closed', 'closed without resolution - end of session, MIA etc.')
    )

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(ArrowType, default=arrow.utcnow())

    status = db.Column(ChoiceType(STATUSES), default='unresolved')
    name = db.Column(db.String(50))
    comments = db.Column(db.Text)
    assignment = db.Column(db.String(25))
    problem = db.Column(db.String(25))
    location = db.Column(db.String(25))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category = db.Column(ChoiceType(CATEGORIES))

    @property
    def owner(self):
        return Owner.query.filter_by(id=self.owner_id).first()
