from flask import Blueprint, request, redirect, url_for, g
from quuupod import app, db
from quuupod.views import requires, render
from quuupod.models import User, Inquiry, Queue, QueueSetting
from quuupod.notifications import *
from quuupod.defaults import default_queue_settings
import flask_login


admin = Blueprint('admin', __name__, url_prefix='/<string:queue_url>/admin',
    template_folder='templates')


@admin.url_defaults
def add_queue_url(endpoint, values):
    values.setdefault('queue_url', getattr(g, 'queue_url', None))


@admin.url_value_preprocessor
def pull_queue_url(endpoint, values):
    g.user = flask_login.current_user
    g.queue_url = values.pop('queue_url')
    g.queue = Queue.query.filter_by(url=g.queue_url).one()


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
    return render_admin('home.html')

@admin.route('/help')
@flask_login.login_required
@requires('staff')
def help():
    """help start"""
    if not g.queue.setting('location_selection').enabled:
        return redirect(url_for('admin.help_latest'))
    locations = [(l,
        Inquiry.query.filter_by(location=l, status='unresolved').count())
        for l in g.queue.setting('locations').value.split(',')]
    return render_admin('help.html',
        no_mobile_action=True,
        locations=[t for t in locations if t[1]],
        current_inquiry=Inquiry.current())

@admin.route('/clear/<string:location>', methods=['POST', 'GET'])
@admin.route('/clear', methods=['POST', 'GET'])
@flask_login.login_required
@requires('staff')
def clear(location=None):
    """Clear all inquiries, period. Or, clear all inquiries for a location."""
    if location:
        return 'Not yet implemented.'
    if request.method == 'POST':
        Inquiry.query.filter_by(status='unresolved').update(
            {'status': 'closed'})
        Inquiry.query.filter_by(status='resolving').update(
            {'status': 'closed'})
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
@requires('staff')
def help_latest(location=None, category=None):
    """automatically selects next inquiry"""
    inquiry = Inquiry.latest(location=location, category=category)
    if not inquiry:
        return redirect(url_for('admin.help', notification=NOTIF_HELP_DONE))
    if g.queue.setting('inquiry_types').enabled and not category:
        categories = [(cat, Inquiry.query.filter_by(
            category=cat, status='unresolved', location=location).count())
            for cat in g.queue.setting('inquiry_types').split(',')]
        categories = [c for c in categories if c[1]]
        if len(categories) > 1:
            return render_admin('categories.html',
                title='Request Type',
                location=location,
                categories=categories)
    delayed_id = request.args.get('delayed_id', None)
    if delayed_id:
        Inquiry.query.get(delayed_id).unlock()
    inquiry.lock()
    inquiry.link(g.user)
    return redirect(url_for('admin.help_inquiry',
        id=inquiry.id, location=location))

@admin.route('/help/inquiry/<string:location>/<string:id>', methods=['POST', 'GET'])
@admin.route('/help/inquiry/<string:id>', methods=['POST', 'GET'])
@flask_login.login_required
@requires('staff')
def help_inquiry(id, location=None):
    """automatically selects next inquiry or reloads inquiry """
    inquiry = Inquiry.query.get(id)
    if request.method == 'POST':
        delayed_id=None
        if request.form['status'] == 'unresolved':
            delayed_id = inquiry.id
            inquiry.resolution.close()
        else:
            inquiry.close()
        if not location:
            return redirect(url_for('admin.help_latest', delayed_id=delayed_id))
        return redirect(url_for('admin.help_latest',
            location=location, delayed_id=delayed_id))
    return render_admin('help_inquiry.html',
        inquiry=inquiry,
        inquiries=Inquiry.query.filter_by(name=inquiry.name).limit(10).all(),
        hide_event_nav=True)


############
# SETTINGS #
############

@admin.route('/settings', methods=['POST', 'GET'])
@flask_login.login_required
@requires('staff')
def settings():
    """settings"""
    settings = QueueSetting.query.join(Queue).filter_by(
        id=g.queue.id).all()
    if request.method == 'POST':
        notification = NOTIF_SETTING_UPDATED
        setting = Setting.query.filter_by(name=request.form['name']).first()
        for k, v in request.form.items():
            setattr(setting, k, v)
        setting.save()
        return redirect(url_for('admin.settings',
            notification=notification))
    return render_admin('settings.html', settings=settings)
