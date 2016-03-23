"""
Important: Changes here need to be followed by `make refresh`.
"""

from quupod import db, tz
from sqlalchemy import types, asc
from sqlalchemy_utils import EncryptedType, PasswordType, ArrowType
from sqlalchemy_utils.types.choice import ChoiceType
from passlib.context import CryptContext
from quupod.defaults import default_queue_settings
import flask_login, arrow
from flask import g, request
from quupod.views import url_for
from quupod.utils import strfdelta

#################
# PARENT MODELS #
#################

_blank = lambda x:x

class Base(db.Model):
    """Base Model for all other models"""

    __abstract__ = True

    __access_token = None
    __context = CryptContext(schemes=['pbkdf2_sha512'])

    id = db.Column(db.Integer, primary_key=True)
    updated_at = db.Column(ArrowType)
    updated_by = db.Column(db.Integer)
    created_at = db.Column(ArrowType, default=arrow.now('US/Pacific'))
    created_by = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)

    def __init__(self, *args, **kwargs):
        super(Base, self).__init__(*args, **kwargs)

    @property
    def entity(self):
        """Returns entity name"""
        return self.__class__.__name__.lower()

    @staticmethod
    def random_hash():
        """Generates random hash"""
        return Base.hash(str(arrow.utcnow()))

    @staticmethod
    def hash(value):
        """Hashes value"""
        return Base.__context.encrypt(value)

    @classmethod
    def from_request(cls):
        """Create object from request"""
        return cls(**dict(request.form.items())).save()

    def modify_time(self, *fields, act=lambda t: t):
        """Modify times"""
        for field in fields:
            setattr(self, field, act(getattr(self, field)))
        return self

    def to_local(self, *fields):
        """Convert all to local times"""
        return self.modify_time(*fields, act=lambda t: t.to(tz or 'local'))

    def to_utc(self, *fields):
        """Convert all to UTC times"""
        return self.modify_time(*fields, act=lambda t: t.to('utc'))

    def set_tz(self, *fields, tz):
        """Set timezones of current times to be a specific tz"""
        return self.modify_time(*fields,
            act=lambda t: t.replace(tzinfo=tz))

    def set_local(self, *fields):
        """Set timezones of current times to be local time"""
        from dateutil import tz as t
        return self.set_tz(*fields, tz=t.gettz(tz) if tz else t.tzlocal())

    def update(self, **kwargs):
        """Update object with kwargs"""
        for k, v in kwargs.items():
            setattr(self, k, v)
        return self

    def save(self):
        """Save object"""
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except:
            db.session.rollback()
            return self.save()

    def setting(self, name, dynamic=False, default=_blank):
        """Get Setting by name"""
        assert name in self.__defaultsettings__ or dynamic, 'Not a valid setting'
        key = {'%s_id' % self.entity: self.id}
        setting = self.__settingclass__.query.filter_by(
            name=name,
            **key).one_or_none()
        if not setting:
            setting = self.load_setting(name, default)
        return setting

    def load_setting(self, name, default=_blank):
        """load a setting"""
        try:
            key = {'%s_id' % self.entity: self.id}
            key.update(self.__defaultsettings__[name])
            key.setdefault('name', name)
            return self.__settingclass__(
                **key).save()
        except KeyError:
            if default == _blank:
                raise UserWarning('No such setting "%s"' % name)
            return default

    def load_settings(self, *names):
        """load a series of settings"""
        return [self.load_setting(n) for n in names]

    def deactivate(self):
        """deactivate"""
        self.is_active = False
        return self.save()

    def activate(self):
        """activate"""
        self.is_active = True
        return self.save()

    def load_roles(self, roles):
        """load role settings"""
        RoleClass = {
            'queue': QueueRole
        }[self.entity]
        for role in roles:
            filt = {
                'name': role['name'],
                '%s_id' % self.entity: self.id
            }
            if not RoleClass.query.filter_by(**filt).one_or_none():
                role = role.copy()
                role.setdefault('%s_id' % self.entity, self.id)
                RoleClass(**role).save()
        return self


class Setting(Base):
    """base setting model"""

    __abstract__ = True

    name = db.Column(db.String(100))
    label = db.Column(db.String(100))
    description = db.Column(db.Text)
    value = db.Column(db.Text)

    toggable = db.Column(db.Boolean, default=False)
    enabled = db.Column(db.Boolean, default=True)
    enable_description = db.Column(db.Text)
    input_type = db.Column(db.String(50), default='text')


class Role(Base):
    """base role model (<- hahaha. punny)"""

    __abstract__ = True

    name = db.Column(db.String(100))
    permissions = db.Column(db.Text)


############
# ENTITIES #
############


class QueueRole(Role):
    """roles for a queue"""

    __tablename__ = 'queue_role'

    queue_id = db.Column(db.Integer, db.ForeignKey('queue.id'))


class QueueSetting(Setting):
    """settings for the queue application"""

    __tablename__ = 'queue_setting'

    queue_id = db.Column(db.Integer, db.ForeignKey('queue.id'))


class Queue(Base):

    __tablename__ = 'queue'
    __settingclass__ = QueueSetting
    __defaultsettings__ = default_queue_settings

    name = db.Column(db.String(50))
    description = db.Column(db.Text)
    url = db.Column(db.String(50), unique=True)
    category = db.Column(db.String(50))
    settings = db.relationship("QueueSetting", backref="queue")

    def present_staff(self):
        """Fetch all present staff members"""
        resolutions = Resolution.query.join(Inquiry).filter(
            Resolution.resolved_at >= arrow.utcnow().replace(hours=-3),
            Inquiry.queue_id == self.id).all()
        staff = set()
        for resolution in resolutions:
            user = User.query.get(resolution.user_id)
            user.resolution = resolution
            ns = [res.resolved_at - res.created_at for res in Resolution.query.filter(
                Resolution.resolved_at >= arrow.utcnow().replace(hours=-6),
                Resolution.user_id == user.id
            )]
            if ns:
                total = ns[0]
                for n in ns[1:]:
                    total = n + total
                user.average = total/len(ns)
            else:
                user.average = 'n/a'
            current = Resolution.query.filter_by(user_id=user.id,
                resolved_at=None).first()
            user.status = 'free' if not current else 'busy'
            staff.add(user)
        return staff

    def ttr(self):
        """Compute average time until resolution."""
        resolutions = Resolution.query.filter(
            Resolution.created_at >= arrow.utcnow().replace(hours=-3)).all()
        ns = [res.created_at - res.inquiry.created_at for res in resolutions]
        if ns:
            total = ns[0]
            for n in ns[1:]:
                total = n + total
            return strfdelta(total/len(ns))
        return '00:00:00'

    def is_valid_assignment(self, request, form):
        """
        Check if the assignment is valid, based on the settings

        :param InquiryForm form: form to check
        :return: boolean
        """
        return not self.setting('assignments').enabled or \
            self.allowed_assignment(request, form)

    def allowed_assignment(self, request, form):
        """
        Returns if assignment is allowed, per settings

        :param InquiryForm form: form to check
        :return: list of assignment names
        """
        lst = self.setting('assignments').value
        str2lst = lambda s: (s.strip() for s in lst.split(','))
        assignment, category = request.form['assignment'], request.form.get('category', None)
        if ':' in lst:
            lst = dict(l.split(':') for l in lst.splitlines()).get(category, '*')
            if lst == '*':
                return True
        if assignment not in str2lst(lst):
            prefix = 'Assignment'
            if category:
                prefix = 'For "%s" inquiries, assignment' % category
            form.errors.setdefault('assignment', []).append('%s "%s" is not allowed. Only the following assignments are: %s' % (prefix, assignment, lst))
            return False
        return True

    @property
    def roles(self):
        """Returns all available roles for this queue"""
        if not getattr(self, '__role', None):
            self.__role = QueueRole.query.filter_by(queue_id=self.id).all()
        return self.__role

class Resolution(Base):

    __tablename__ = 'resolution'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    inquiry_id = db.Column(db.Integer, db.ForeignKey('inquiry.id'), index=True)
    resolved_at = db.Column(ArrowType, index=True)
    comment = db.Column(db.Text)

    @property
    def inquiry(self):
        return Inquiry.query.filter_by(id=self.inquiry_id).first()

    @property
    def staff(self):
        return User.query.filter_by(id=self.user_id).first()

    def close(self):
        """close resolution"""
        self.resolved_at = arrow.utcnow()
        return self.save()


class User(Base, flask_login.UserMixin):
    """queue system user"""

    __tablename__ = 'user'

    inquiries = db.relationship('Inquiry', backref='owner', lazy='dynamic')
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(PasswordType(schemes=['pbkdf2_sha512']))
    image_url = db.Column(db.Text)

    google_id = db.Column(db.String(30), unique=True)

    @property
    def role(self):
        """Get user role for given queue"""
        return QueueRole.query.join(Participant).filter_by(
            queue_id=g.queue.id,
            user_id=self.id,
            is_active=True).one_or_none()

    @staticmethod
    def get_home(user, **kwargs):
        """Return home URL for given user"""
        if getattr(g, 'queue', None):
            if user and user.can('admin'):
                return url_for('admin.home', **kwargs)
            return url_for('queue.home', **kwargs)
        return url_for('dashboard.home')

    def set_role(self, role):
        """set role for user"""
        part = Participant.query.filter_by(
            queue_id=g.queue.id,
            user_id=self.id,
            is_active=True).one_or_none()
        role_id = QueueRole.query.filter_by(
            queue_id=g.queue.id, name=role).one().id
        if part:
            part.role_id = role_id
            return part.save()
        return Participant(
            queue_id=g.queue.id,
            user_id=self.id,
            role_id=role_id
        ).save()

    def join(self, queue, role=None, role_id=None):
        """Join a queue"""
        assert queue.id, 'Save queue object first'
        assert isinstance(queue, Queue), 'Can only join group.'
        role_id = role_id or QueueRole.query.filter_by(
            name=role,
            queue_id=queue.id
        ).one().id
        return Participant(
            user_id=self.id,
            queue_id=queue.id,
            role_id=role_id).save()

    def queues(self):
        """returns all queues for this user"""
        return Queue.query.join(Participant).filter_by(user_id=self.id).all()

    def can(self, permission):
        role = self.role
        if role and \
            (role.permissions == '*' or \
            permission in role.permissions.split(',')):
            return True
        return False


class Inquiry(Base):
    """inquiry placed in queue"""

    __tablename__ = 'inquiry'

    STATUSES = (
        ('unresolved', 'has not yet been addressed'),
        ('resolving', 'being addressed by admin'),
        ('resolved', 'addressed and closed'),
        ('closed', 'closed without resolution - end of session, MIA etc.')
    )

    status = db.Column(ChoiceType(STATUSES), default='unresolved', index=True)
    name = db.Column(db.String(50))
    comments = db.Column(db.Text)
    assignment = db.Column(db.String(25))
    problem = db.Column(db.String(25))
    location = db.Column(db.String(25))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category = db.Column(db.String(25), default='question')
    queue_id = db.Column(db.Integer, db.ForeignKey('queue.id'), index=True)

    @staticmethod
    def current():
        resolution = Resolution.query.filter_by(
            user_id=flask_login.current_user.id,
            resolved_at=None).first()
        if resolution:
            return resolution.inquiry

    @staticmethod
    def latest(**kwargs):
        current_inquiry = Inquiry.current()
        if current_inquiry:
            return current_inquiry
        kwargs = {k:v for k, v in kwargs.items() if v}
        return Inquiry.query.filter_by(
            status='unresolved',
            queue_id=g.queue.id,
            **kwargs).order_by(asc(Inquiry.created_at)).first()

    @property
    def resolution(self):
        if self.status != 'resolved':
            return Resolution.query.filter_by(
            resolved_at=None, inquiry_id=self.id).first()
        else:
            return Resolution.query.filter_by(inquiry_id=self.id).first()

    @property
    def owner(self):
        return Owner.query.filter_by(id=self.owner_id).first()

    def unlock(self):
        """Unlock Inquiry and re-enqueue request."""
        self.status = 'unresolved'
        if self.resolution:
            self.resolution.close()
        return self.save()

    def lock(self):
        """Lock an Inquiry, so no other staff members can attempt to resolve."""
        self.status = 'resolving'
        return self.save()

    def close(self):
        """Close an Inquiry"""
        self.status = 'resolved'
        return self.save()

    def link(self, user):
        """link inquiry to a user."""
        if not Resolution.query.filter_by(
            user_id=user.id, inquiry_id=self.id,
        resolved_at=None).one_or_none():
            return Resolution(user_id=user.id, inquiry_id=self.id).save()


##############################
# MANY-TO-MANY RELATIONSHIPS #
##############################

class Participant(Base):

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    queue_id = db.Column(db.Integer, db.ForeignKey('queue.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('queue_role.id'))

    @property
    def role(self):
        return QueueRole.query.get(self.role_id)
