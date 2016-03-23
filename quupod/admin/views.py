from flask import Blueprint, request, redirect, g, abort
from quupod import app, db
from quupod.views import requires, render, url_for, current_user
from quupod.models import User, Inquiry, Queue, QueueSetting, Participant
from quupod.notifications import *
from quupod.defaults import default_queue_settings
from quupod.utils import strfdelta
import flask_login
import arrow


admin = Blueprint('admin', __name__, url_prefix='/<string:queue_url>/admin',
    template_folder='templates')


@admin.url_defaults
def add_queue_url(endpoint, values):
    values.setdefault('queue_url', getattr(g, 'queue_url', None))


@admin.url_value_preprocessor
def pull_queue_url(endpoint, values):
    g.queue_url = values.pop('queue_url')
    g.queue = Queue.query.filter_by(url=g.queue_url).one_or_none()
    if not g.queue:
        abort(404)
    if current_user().is_authenticated:
        g.participant = Participant.query.filter_by(user_id=current_user().id, queue_id=g.queue.id).one_or_none()


def render_admin(template, *args, **kwargs):
    """Special rendering for queue admin"""
    for k in default_queue_settings:
        setting = g.queue.setting(k)
        kwargs.update({'q_%s' % k: setting.value or setting.enabled})
    kwargs.setdefault('queue', g.queue)
    return render(template, *args, **kwargs)


#########
# ADMIN #
#########

@admin.route('/')
@flask_login.login_required
@requires('staff')
def home():
    """admin homepage"""
    if not g.queue.setting('location_selection').enabled:
        return render_admin('home.html',
            latest_inquiry=Inquiry.latest(),
            current_inquiry=Inquiry.current(),
            ttr=g.queue.ttr())
    locations = [(l,
        Inquiry.query.filter_by(
            location=l, status='unresolved', queue_id=g.queue.id).count())
        for l in g.queue.setting('locations').value.split(',')]
    return render_admin('home.html',
        locations=[t for t in locations if t[1]],
        current_inquiry=Inquiry.current(),
        ttr=g.queue.ttr())


@admin.route('/clear/<string:location>', methods=['POST', 'GET'])
@admin.route('/clear', methods=['POST', 'GET'])
@flask_login.login_required
@requires('help')
def clear(location=None):
    """Clear all inquiries, period. Or, clear all inquiries for a location."""
    if location:
        return 'Not yet implemented.'
    if request.method == 'POST':
        Inquiry.query.filter_by(
            status='unresolved',
            queue_id=g.queue.id).update({'status': 'closed'})
        Inquiry.query.filter_by(
            status='resolving',
            queue_id=g.queue.id).update({'status': 'closed'})
        db.session.commit()
        return render_admin('admin_confirm.html',
            message='All Cleared',
            action='Admin Home',
            url=url_for('admin.home'))
    return render_admin('admin_confirm.html',
        message='Are you sure? This will clear all resolving and unresolved. \
        <form method="POST"><input type="submit" value="clear"></form>',
        action='admin home',
        url=url_for('admin.home'))

@admin.route('/help/<string:location>/<string:category>/latest', methods=['POST', 'GET'])
@admin.route('/help/<string:location>/latest')
@admin.route('/help/latest')
@flask_login.login_required
@requires('help')
def help_latest(location=None, category=None):
    """automatically selects next inquiry"""
    inquiry = Inquiry.latest(location=location, category=category)
    delayed_id, delayed = request.args.get('delayed_id', None), None
    if not inquiry:
        return redirect(url_for('admin.home', notification=NOTIF_HELP_DONE))
    if g.queue.setting('inquiry_types').enabled and not category and g.queue.setting('inquiry_type_selection').enabled:
        categories = [(cat, Inquiry.query.filter_by(
            category=cat,
            status='unresolved',
            location=location,
            queue_id=g.queue.id).count())
            for cat in g.queue.setting('inquiry_types').value.split(',')]
        categories = [c for c in categories if c[1]]
        if len(categories) > 1:
            return render_admin('categories.html',
                title='Request Type',
                location=location,
                categories=categories)
    if delayed_id:
        delayed = Inquiry.query.get(delayed_id)
        delayed.unlock()
    inquiry.lock()
    inquiry.link(current_user())
    return redirect(url_for('admin.help_inquiry',
        id=inquiry.id, location=location))

@admin.route('/help/inquiry/<string:location>/<string:id>', methods=['POST', 'GET'])
@admin.route('/help/inquiry/<string:id>', methods=['POST', 'GET'])
@flask_login.login_required
@requires('help')
def help_inquiry(id, location=None):
    """automatically selects next inquiry or reloads inquiry """
    inquiry = Inquiry.query.get(id)
    if not inquiry.resolution:
        inquiry.lock()
        inquiry.link(current_user())
    if request.method == 'POST':
        delayed_id=None
        inquiry.resolution.close()
        if request.form['status'] == 'unresolved':
            delayed_id = inquiry.id
        else:
            inquiry.close()
        if request.form['load_next'] != 'y':
            if delayed_id:
                delayed = Inquiry.query.get(delayed_id)
                delayed.unlock()
            return redirect(url_for('admin.home'))
        if not location:
            return redirect(url_for('admin.help_latest', delayed_id=delayed_id))
        return redirect(url_for('admin.help_latest',
            location=location, delayed_id=delayed_id))
    return render_admin('help_inquiry.html',
        inquiry=inquiry,
        inquiries=Inquiry.query.filter_by(name=inquiry.name).limit(10).all(),
        hide_event_nav=True,
        group=Inquiry.query.filter(
            Inquiry.status == 'unresolved',
            Inquiry.queue_id == g.queue.id,
            Inquiry.assignment == inquiry.assignment,
            Inquiry.problem == inquiry.problem,
            Inquiry.owner_id != inquiry.owner_id
        ).all(),
        wait_time=strfdelta(
            inquiry.resolution.created_at-inquiry.created_at, '%h:%m:%s'))


############
# SETTINGS #
############

@admin.route('/settings', methods=['POST', 'GET'])
@flask_login.login_required
@requires('edit_settings')
def settings():
    """settings"""
    settings = sorted(QueueSetting.query.join(Queue).filter_by(
        id=g.queue.id).all(), key=lambda s: s.name)
    if g.participant.role.name.lower() != 'owner':
        settings = [s for s in settings if s.name != 'whitelist']
    for setting in settings:
        if setting.name in default_queue_settings:
            # NOTE: this will filter out settings not in the default settings list
            default_description = default_queue_settings[setting.name]['description']
            if default_description != setting.description:
                setting.description = default_description
    if request.method == 'POST':
        notification = NOTIF_SETTING_UPDATED
        setting = QueueSetting.query.filter_by(
            queue_id=g.queue.id,
            name=request.form['name']).first()
        for k, v in request.form.items():
            setattr(setting, k, v)
        if setting.name == 'locations':
            setting.value = setting.value.replace(' ','')
        setting.save()
        return redirect(url_for('admin.settings',
            notification=notification))
    return render_admin('settings.html', settings=settings)
