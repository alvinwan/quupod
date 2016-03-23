from flask import Blueprint, request, g, redirect,\
    abort, session
from .forms import *
from quupod import app, login_manager, whitelist
from quupod.models import User, Inquiry, QueueRole, Participant
from quupod.views import anonymous_required, render, current_user, url_for, current_user, requires
from quupod.forms import choicify
from quupod.defaults import default_queue_settings
from quupod.notifications import *
from sqlalchemy import desc
import flask_login

queue = Blueprint('queue', __name__, url_prefix='/<string:queue_url>',
    template_folder='templates')


@queue.url_defaults
def add_queue_url(endpoint, values):
    values.setdefault('queue_url', getattr(g, 'queue_url', None))


@queue.url_value_preprocessor
def pull_queue_url(endpoint, values):
    g.queue_url = values.pop('queue_url')
    g.queue = Queue.query.filter_by(url=g.queue_url).one_or_none()
    if not g.queue:
        abort(404)


def render_queue(template, *args, **kwargs):
    """Special rendering for queue"""
    whitelist = g.queue.setting('whitelist').value
    if whitelist:
        entries = {}
        for entry in whitelist.split(','):
            entry = tuple(s.strip() for s in entry.split('('))
            if len(entry) == 2:
                entries[entry[0]] = entry[1][:-1]
            else:
                entries[entry[0]] = 'Staff'
        if current_user().is_authenticated and \
            current_user().email in entries:
            current_user().set_role(entries[current_user().email])
    for k in default_queue_settings:
        setting = g.queue.setting(k)
        kwargs.update({'q_%s' % k: setting.value or setting.enabled})
    kwargs.setdefault('queue', g.queue)
    return render(template, *args, **kwargs)


#########
# QUEUE #
#########

@queue.route('/')
def home():
    """list all unresolved inquiries for the homepage"""
    if current_user().can('admin'):
        return redirect(url_for('admin.home'))
    return render_queue('unresolved.html',
        inquiries=Inquiry.query.filter_by(
            status='unresolved',
            queue_id=g.queue.id).all(),
        ttr=g.queue.ttr())

@queue.route('/resolving')
def resolving():
    """List of all 'resolving' inquiries for the homepage"""
    return render_queue('resolving.html',
        inquiries=Inquiry.query.filter_by(
            status='resolving',
            queue_id=g.queue.id).all(),
        panel='Resolving',
        empty='No inquiries currently being resolved.',
        ttr=g.queue.ttr())

@queue.route('/resolved')
def resolved():
    """List of all 'resoled' inquiries for the homepage"""
    return render_queue('resolved.html',
        inquiries=Inquiry.query.filter_by(
            status='resolved',
            queue_id=g.queue.id).order_by(desc(Inquiry.id)).limit(20).all(),
        panel='Resolved',
        empty='No inquiries resolved.',
        ttr=g.queue.ttr())

@queue.route('/staff')
def staff():
    """Lists all staff present at the current event."""
    return render_queue('staff.html',
        staff=g.queue.present_staff(),
        panel='Staff',
        empty='No staff members currently present.',
        ttr=g.queue.ttr())

@queue.route('/promote/<string:role_name>', methods=['POST', 'GET'])
@queue.route('/promote')
def promote(role_name=None):
    """Promote the user accessing this page."""
    if not current_user().is_authenticated:
        return render_queue('error.html',
            code='Oops',
            message='You need to be logged in to promote an account!')
    part = Participant.query.filter_by(
        queue_id=g.queue.id,
        user_id=current_user().id
    ).one_or_none()
    n_owners = Participant.query.join(QueueRole).filter(
        QueueRole.name == 'Owner',
        Participant.queue_id == g.queue.id
    ).count()
    if part and part.role.name == 'Owner' and n_owners <= 1:
        return render_queue('error.html',
            code='Oops',
            message='You cannot demote yourself from owner until another owner has been added.')
    promotion_setting = g.queue.setting(name='self_promotion', default=None)
    if not promotion_setting or not promotion_setting.enabled:
        abort(404)
    tuples = [s.split(':') for s in promotion_setting.value.splitlines()]
    codes = dict((k.strip().lower(), v.strip()) for k, v in tuples)
    role_names = [role.name for role in g.queue.roles]
    if n_owners == 0:
        role_name = 'Owner'
    roles = [s.lower() for s in role_names + list(codes.keys())]
    if role_name and role_name.lower() not in roles:
        abort(404)
    if not role_name:
        return render_queue('roles.html',
            title='Promotion Form',
            message='Welcome. Please select a role below.',
            roles=[name for name in role_names if name.lower() in codes])
    try:
        if n_owners == 0:
            code = '*'
        else:
            code = codes[role_name.lower()]
    except KeyError:
        abort(404)
    form = PromotionForm(request.form)
    if request.method == 'POST' or code == '*':
        role = QueueRole.query.filter_by(
            name=role_name, queue_id=g.queue.id).one()
        if code == '*' or request.form['code'] == code:
            part = Participant.query.filter_by(
                user_id=current_user().id,
                queue_id=g.queue.id).one_or_none()
            if part:
                part.update(role_id = role.id).save()
            else:
                Participant(
                    user_id=current_user().id,
                    queue_id=g.queue.id,
                    role_id=role.id
                ).save()
        else:
            form.errors.setdefault('code', []).append('Incorrect code.')
            return render_queue('form.html',
                form=form,
                submit='Promote',
                back=url_for('queue.promote'))
        return render_queue('confirm.html',
            title='Promotion Success',
            message='You have been promoted to %s' % role_name,
            action='back',
            url=url_for('queue.home'))
    return render_queue('form.html',
        form=form,
        submit='Promote')

@queue.route('/request', methods=['POST', 'GET'])
def inquiry():
    """
    Place a new request, which may be authored by either a system user or an
    anonymous user.
    """
    user, form = flask_login.current_user, InquiryForm(request.form)
    if user.is_authenticated:
        form = InquiryForm(request.form, obj=user)
    elif g.queue.setting(name='require_login').enabled:
        return render_queue('confirm.html',
            title='Login Required',
            message='Login to add an inquiry, and start using this queue.')
    n = int(g.queue.setting(name='max_requests').value)
    filter_id = User.email == current_user().email if \
        current_user().is_authenticated else User.name == request.form.get('name', None)
    not_logged_in_max = ''
    if Inquiry.query.join(User).filter(
        filter_id,
        Inquiry.status=='unresolved',
        Inquiry.queue_id==g.queue.id
        ).count() >= n:
        if not current_user().is_authenticated:
            not_logged_in_max = 'If you haven\'t submitted a request, try logging in and re-requesting.'
        return render_queue('confirm.html',
            title='Oops',
            message='Looks like you\'ve reached the maximum number of times you can add yourself to the queue at once (<code>%d</code>). %s' % (n, not_logged_in_max),
            action='Back',
            url=url_for('queue.home'))
    form.location.choices = choicify(
        g.queue.setting('locations').value.split(','))
    form.category.choices = choicify(
        g.queue.setting('inquiry_types').value.split(','))
    if request.method == 'POST' and form.validate() and \
        g.queue.is_valid_assignment(request, form):
        inquiry = Inquiry(**request.form)
        inquiry.queue_id = g.queue.id
        if current_user().is_authenticated:
            inquiry.owner_id = current_user().id
        inquiry.save()
        return redirect(url_for('queue.home',
            notification=NOTIF_INQUIRY_PLACED))
    return render_queue('form.html', form=form, title='Request Help',
        submit='Request Help')

@queue.route('/requeue/<int:inquiry_id>', methods=['POST', 'GET'])
@requires('help')
def requeue(inquiry_id):
    delayed = Inquiry.query.get(inquiry_id)
    delayed.unlock()
    return redirect(url_for('queue.resolved'))


################
# LOGIN/LOGOUT #
################

@queue.route('/login', methods=['POST', 'GET'])
def login():
    """Login using globally defined login procedure"""
    from quupod.public.views import login
    return login(
        home=url_for('queue.home', _external=True),
        login=url_for('queue.login', _external=True))

@queue.route('/logout')
def logout():
    """Logout using globally defined logout procedure"""
    from quupod.public.views import logout
    return logout()
