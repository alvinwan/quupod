"""All models for the queue.

Important: Changes here need to be followed by `make refresh`.
"""

from sqlalchemy import asc
from flask import current_app
from werkzeug.local import LocalProxy
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import PasswordType
from sqlalchemy_utils import ArrowType
from sqlalchemy_utils.types.choice import ChoiceType
from passlib.context import CryptContext
from quupod.defaults import default_queue_settings
import flask_login
import arrow
from flask_script import Manager
from flask_migrate import Migrate
from flask import g, request
from quupod.views import url_for
from quupod.utils import strfdelta
from quupod.utils import Nil
from wtforms import Form

#################
# PARENT MODELS #
#################

db = SQLAlchemy()
migrate = Migrate()
migration_manager = Manager()
toolbar = DebugToolbarExtension()


class Base(db.Model):
    """Base Model for all other models."""

    __abstract__ = True

    __access_token = None
    __context = CryptContext(schemes=['pbkdf2_sha512'])

    id = db.Column(db.Integer, primary_key=True)
    updated_at = db.Column(ArrowType)
    updated_by = db.Column(db.Integer)
    created_at = db.Column(ArrowType, default=arrow.now('US/Pacific'))
    created_by = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)

    @property
    def entity(self) -> str:
        """Return entity name."""
        return self.__class__.__name__.lower()

    @staticmethod
    def random_hash() -> str:
        """Generate random hash."""
        return Base.hash(str(arrow.utcnow()))

    @staticmethod
    def hash(value: str) -> str:
        """Hash value.

        :param value: The value to hash.
        """
        return Base.__context.encrypt(value)

    @classmethod
    def from_request(cls):
        """Create object from request."""
        return cls(**dict(request.form.items())).save()

    def modify_time(self, *fields, act=lambda t: t) -> db.Model:
        """Modify times.

        :param *fields: The fields to change to local times.
        :param act: A function to modify all time values.
        """
        for field in fields:
            setattr(self, field, act(getattr(self, field)))
        return self

    def to_local(self, *fields) -> db.Model:
        """Convert all to local times.

        :param *fields: The fields to change to local times.
        """
        return self.modify_time(
            *fields,
            act=lambda t: t.to(current_app.config['TZ'] or 'local'))

    def to_utc(self, *fields) -> db.Model:
        """Convert all to UTC times.

        :param *fields: The fields to change to UTC time.
        """
        return self.modify_time(*fields, act=lambda t: t.to('utc'))

    def set_tz(self, *fields, tz: str) -> db.Model:
        """Set timezones of current times to be a specific tz.

        :param *fields: The fields to change to the specified timezone.
        :param tz: The timezone.
        """
        return self.modify_time(
            *fields,
            act=lambda t: t.replace(tzinfo=tz))

    def set_local(self, *fields) -> db.Model:
        """Set timezones of current times to be local time.

        :param *fields: The fields to change to local time.
        """
        from dateutil import tz as t
        return self.set_tz(
            *fields,
            tz=t.gettz(current_app.config['TZ']) or t.tzlocal())

    def update(self, **kwargs) -> db.Model:
        """Update object with kwargs."""
        for k, v in kwargs.items():
            setattr(self, k, v)
        return self

    def save(self) -> db.Model:
        """Save object."""
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except:
            db.session.rollback()
            return self.save()

    def setting(
            self,
            name: str,
            dynamic: bool=False,
            default=Nil) -> db.Model:
        """Get Setting by name.

        :param name: The name of the setting to fetch.
        :param dynamic: Set to true if the setting is not expected to exist in
                        default
        """
        assert name in self.__defaultsettings__ or dynamic, \
            'Not a valid setting'
        key = {'%s_id' % self.entity: self.id}
        setting = self.__settingclass__.query.filter_by(
            name=name,
            **key).one_or_none()
        if not setting:
            setting = self.load_setting(name, default)
        return setting

    def load_setting(self, name: str, default=Nil) -> db.Model:
        """Load a setting."""
        try:
            key = {'%s_id' % self.entity: self.id}
            key.update(self.__defaultsettings__[name])
            key.setdefault('name', name)
            return self.__settingclass__(
                **key).save()
        except KeyError:
            if default == Nil:
                raise UserWarning('No such setting "%s"' % name)
            return default

    def load_settings(self, *names) -> [db.Model]:
        """Load a series of settings."""
        return [self.load_setting(n) for n in names]

    def deactivate(self) -> db.Model:
        """Deactivate the object."""
        self.is_active = False
        return self.save()

    def activate(self) -> db.Model:
        """Activate the object."""
        self.is_active = True
        return self.save()

    def load_roles(self, roles: [str]) -> db.Model:
        """Load role settings."""
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
    """Base setting model."""

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
    """Base role model (<- hahaha. punny)."""

    __abstract__ = True

    name = db.Column(db.String(100))
    permissions = db.Column(db.Text)


############
# ENTITIES #
############


class QueueRole(Role):
    """Roles for a queue."""

    __tablename__ = 'queue_role'

    queue_id = db.Column(db.Integer, db.ForeignKey('queue.id'))


class QueueSetting(Setting):
    """Settings for the queue application."""

    __tablename__ = 'queue_setting'

    queue_id = db.Column(db.Integer, db.ForeignKey('queue.id'))


class Queue(Base):
    """Model for all queues."""

    __tablename__ = 'queue'
    __settingclass__ = QueueSetting
    __defaultsettings__ = default_queue_settings

    name = db.Column(db.String(50))
    description = db.Column(db.Text)
    url = db.Column(db.String(50), unique=True)
    category = db.Column(db.String(50))
    settings = db.relationship("QueueSetting", backref="queue")

    def present_staff(self) -> {db.Model}:
        """Fetch all present staff members."""
        resolutions = Resolution.query.join(Inquiry).filter(
            Resolution.resolved_at >= arrow.utcnow().replace(hours=-3),
            Inquiry.queue_id == self.id).all()
        staff = set()
        for resolution in resolutions:
            user = User.query.get(resolution.user_id)
            user.resolution = resolution
            ns = [
                res.resolved_at - res.created_at
                for res in Resolution.query.filter(
                    Resolution.resolved_at >= arrow.utcnow().replace(hours=-6),
                    Resolution.user_id == user.id)]
            if ns:
                total = ns[0]
                for n in ns[1:]:
                    total = n + total
                user.average = total/len(ns)
            else:
                user.average = 'n/a'
            current = Resolution.query.filter_by(
                user_id=user.id,
                resolved_at=None).first()
            user.status = 'free' if not current else 'busy'
            staff.add(user)
        return staff

    def ttr(self) -> str:
        """Compute average time until resolution."""
        resolutions = Resolution.query.join(Inquiry).filter(
            Resolution.created_at >= arrow.utcnow().replace(hours=-3),
            Inquiry.queue_id == self.id).all()
        ns = [res.created_at - res.inquiry.created_at for res in resolutions]
        if ns:
            total = ns[0]
            for n in ns[1:]:
                total = n + total
            return strfdelta(total/len(ns))
        return '00:00:00'

    def is_valid_assignment(self, request: LocalProxy, form: Form) -> bool:
        """Check if the assignment is valid, based on settings.

        :param request: The request context object.
        :param form: form to check
        """
        return not self.setting('assignments').enabled or \
            self.allowed_assignment(request, form)

    def allowed_assignment(self, request: LocalProxy, form: Form) -> bool:
        """Return if assignment is allowed, per settings.

        :param request: The request context object.
        :param form: form to check
        """
        lst = self.setting('assignments').value
        assignment = request.form['assignment']
        category = request.form.get('category', None)
        if ':' in lst:
            datum = dict(l.split(':') for l in lst.splitlines())
            if datum.get(category, '*') == '*':
                return True
        if assignment not in [s.strip() for s in lst.split(',')]:
            prefix = 'Assignment'
            if category:
                prefix = 'For "%s" inquiries, assignment' % category
            form \
                .errors \
                .setdefault('assignment', []) \
                .append(
                    '%s "%s" is not allowed. Only the following '
                    'assignments are: %s' % (prefix, assignment, lst))
            return False
        return True

    @property
    def roles(self) -> [Role]:
        """Return all available roles for this queue."""
        if not getattr(self, '__role', None):
            self.__role = QueueRole.query.filter_by(queue_id=self.id).all()
        return self.__role


class Resolution(Base):
    """Model for a resolution object.

    A resolution object is created any time an inquiry it closed; it is NOT
    created if the inquiry is re-queued however.
    """

    __tablename__ = 'resolution'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    inquiry_id = db.Column(
        db.Integer,
        db.ForeignKey('inquiry.id'),
        index=True)
    resolved_at = db.Column(ArrowType, index=True)
    comment = db.Column(db.Text)

    @property
    def inquiry(self):
        """Fetch the related inquiry for this resolution."""
        return Inquiry.query.get(self.inquiry_id)

    @property
    def staff(self):
        """Fetch the related staff member for this resolution."""
        return User.query.get(self.user_id)

    def close(self):
        """Close resolution."""
        self.resolved_at = arrow.utcnow()
        return self.save()


class User(Base, flask_login.UserMixin):
    """Queue system user."""

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
        """Get user role for given queue."""
        return QueueRole.query.join(Participant).filter_by(
            queue_id=g.queue.id,
            user_id=self.id,
            is_active=True).one_or_none()

    @staticmethod
    def get_home(user: db.Model, **kwargs) -> str:
        """Return home URL for given user."""
        if getattr(g, 'queue', None):
            if user and user.can('admin'):
                return url_for('admin.home', **kwargs)
            return url_for('queue.home', **kwargs)
        return url_for('dashboard.home')

    def set_role(self, role: str) -> db.Model:
        """set role for user."""
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

    def join(
            self,
            queue: Queue,
            role: str=None,
            role_id: str=None) -> db.Model:
        """Join a queue."""
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
        """Return all queues for this user."""
        return Queue \
            .query \
            .join(Participant) \
            .filter_by(user_id=self.id) \
            .all()

    def can(self, *permission):
        """Check permissions for this user."""
        role = self.role
        if role and \
            (role.permissions == '*' or
             any(p in role.permissions.split(',') for p in permission)):
            return True
        return False


class Inquiry(Base):
    """Inquiry placed in queue."""

    __tablename__ = 'inquiry'

    STATUSES = (
        ('unresolved', 'has not yet been addressed'),
        ('resolving', 'being addressed by admin'),
        ('resolved', 'addressed and closed'),
        ('closed', 'closed without resolution - end of session, MIA etc.'))

    status = db.Column(
        ChoiceType(STATUSES),
        default='unresolved',
        index=True)
    name = db.Column(db.String(50))
    comments = db.Column(db.Text)
    assignment = db.Column(db.String(25))
    problem = db.Column(db.String(25))
    location = db.Column(db.String(25))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category = db.Column(db.String(25), default='question')
    queue_id = db.Column(db.Integer, db.ForeignKey('queue.id'), index=True)

    @staticmethod
    def current() -> Resolution:
        """Return current resolution for the logged-in user."""
        resolution = Resolution.query.filter_by(
            user_id=flask_login.current_user.id,
            resolved_at=None).first()
        if resolution:
            return resolution.inquiry

    @staticmethod
    def latest(**kwargs) -> db.Model:
        """Return latest inquiry."""
        current_inquiry = Inquiry.current()
        if current_inquiry:
            return current_inquiry
        kwargs = {k: v for k, v in kwargs.items() if v}
        return Inquiry.query.filter_by(
            status='unresolved',
            queue_id=g.queue.id,
            **kwargs).order_by(asc(Inquiry.created_at)).first()

    @property
    def queue(self) -> Queue:
        """Return associated queue."""
        return Queue.query.get(self.queue_id)

    @property
    def resolution(self) -> Resolution:
        """Return the resolution associated with this inquiry."""
        if self.status != 'resolved':
            return Resolution.query.filter_by(
                resolved_at=None,
                inquiry_id=self.id).first()
        else:
            return Resolution.query.filter_by(inquiry_id=self.id).first()

    @property
    def owner(self):
        """The user that filed the inquiry."""
        return User.query.get(self.owner_id)

    def unlock(self):
        """Unlock Inquiry and re-enqueue request."""
        self.status = 'unresolved'
        if self.resolution:
            self.resolution.close()
        return self.save()

    def lock(self):
        """Lock an inquiry.

        This is so no other staff members can attempt to resolve.
        """
        self.status = 'resolving'
        return self.save()

    def close(self):
        """Close an inquiry."""
        self.status = 'resolved'
        return self.save()

    def link(self, user):
        """Link inquiry to a user."""
        if not Resolution.query.filter_by(
                user_id=user.id,
                inquiry_id=self.id,
                resolved_at=None).one_or_none():
            return Resolution(user_id=user.id, inquiry_id=self.id).save()


##############################
# MANY-TO-MANY RELATIONSHIPS #
##############################

class Participant(Base):
    """A participant represents a user for a queue.

    This may be a staff member, a member requesting help, or even the
    owner.
    """

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    queue_id = db.Column(db.Integer, db.ForeignKey('queue.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('queue_role.id'))

    @property
    def role(self):
        """Return the role associated with this participant."""
        return QueueRole.query.get(self.role_id)
