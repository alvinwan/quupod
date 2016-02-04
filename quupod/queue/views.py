from flask import Blueprint, request, g, redirect,\
    abort
from .forms import *
from quupod import app, login_manager, whitelist
from quupod.models import User, Inquiry
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
    return render_queue('unresolved.html',
        inquiries=Inquiry.query.filter_by(
            status='unresolved',
            queue_id=g.queue.id).all(),
        panel='Unresolved',
        empty='No inquiries have been unaddressed!',
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
            message='Login to add an inquiry, and start using this queue.',
            action='Login',
            url=url_for('queue.login'))
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
        submit='Ask')

@queue.route('/requeue/<int:inquiry_id>', methods=['POST', 'GET'])
@requires('help')
def requeue(inquiry_id):
    delayed = Inquiry.query.get(inquiry_id)
    delayed.unlock()
    return redirect(url_for('queue.resolved'))


################
# LOGIN/LOGOUT #
################

@queue.route('/logout')
def logout():
    from quupod.public.views import logout
    return logout()


@queue.route('/tokenlogin', methods=['POST'])
def token_login():
    from quupod.public.views import token_login
    return token_login()
