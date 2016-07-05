"""Views for the queue admin panel."""

from flask import Blueprint
from flask import request
from flask import redirect
from flask import g
from flask import abort
from quupod import socketio
from quupod.views import requires
from quupod.views import render
from quupod.views import url_for
from quupod.views import current_user
from quupod.models import Inquiry
from quupod.models import Queue
from quupod.models import QueueSetting
from quupod.models import Participant
from quupod.models import Resolution
from quupod.models import db
from quupod.notifications import NOTIF_HELP_DONE
from quupod.notifications import NOTIF_SETTING_UPDATED
from quupod.defaults import default_queue_settings
from quupod.utils import strfdelta
from quupod.utils import emitQueuePositions
from quupod.utils import emitQueueInfo
from quupod.utils import str2lst
from sqlalchemy import desc
import flask_login


admin = Blueprint(
    'admin',
    __name__,
    url_prefix='/<string:queue_url>/admin',
    template_folder='templates')


@admin.url_defaults
def add_queue_url(endpoint: str, values: dict) -> None:
    """Populate URL automatically with current queue."""
    values.setdefault('queue_url', getattr(g, 'queue_url', None))


@admin.url_value_preprocessor
def pull_queue_url(endpoint: str, values: dict) -> None:
    """Pull values from URL automatically."""
    g.queue_url = values.pop('queue_url')
    g.queue = Queue.query.filter_by(url=g.queue_url).one_or_none()
    if not g.queue:
        abort(404)
    if current_user().is_authenticated:
        g.participant = Participant.query.filter_by(
            user_id=current_user().id,
            queue_id=g.queue.id).one_or_none()


def render_admin(template: str, *args, **kwargs) -> str:
    """Special rendering for queue admin."""
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
@requires('help')
def home() -> str:
    """The queue administration home page."""
    context = {
        'num_inquiries': Inquiry.count_unresolved(),
        'latest_inquiry': Inquiry.current_or_latest(),
        'current_inquiry': Inquiry.current(),
        'ttr': g.queue.ttr(),
        'earliest_request': Inquiry.earliest()
    }
    if not g.queue.setting('location_selection').enabled:
        return render_admin('home.html', **context)
    context['locations'] = Inquiry.get_unresolved(
        str2lst(g.queue.setting('locations').value))
    return render_admin('home.html', **context)

##########
# QUEUES #
##########


@admin.route('/unresolved')
@requires('help')
def unresolved() -> str:
    """List all 'unresolved' inquiries."""
    return render_admin(
        'unresolved.html',
        inquiries=Inquiry.get_inquiries(status='unresolved', limit=20))


@admin.route('/resolved')
@requires('help')
def resolved() -> str:
    """List all 'resolved' inquiries."""
    return render_admin(
        'resolved.html',
        inquiries=Inquiry.get_inquiries(status='resolved', limit=20))


@admin.route('/requeue/<int:inquiry_id>', methods=['POST', 'GET'])
@requires('help')
def requeue(inquiry_id: str) -> str:
    """Requeue the provided inquiry."""
    delayed = Inquiry.query.get(inquiry_id)
    delayed.unlock()
    emitQueuePositions(delayed)
    emitQueueInfo(delayed.queue)
    return redirect(url_for('admin.resolved'))


@admin.route('/clear', methods=['POST', 'GET'])
@flask_login.login_required
@requires('help')
def clear() -> str:
    """Clear all inquiries, period."""
    context = {'action': 'Admin Home', 'url': url_for('admin.home')}
    if request.method == 'POST':
        Inquiry.clear_all_inquiries()
        context['message'] = 'All Cleared'
        return render_admin('admin_confirm.html', **context)
    context['message'] = 'Are you sure? This will clear all resolving and'
    'unresolved.<form method="POST"><input type="submit" value="clear"></form>'
    return render_admin('admin_confirm.html', **context)

########
# HELP #
########


# TODO: cleanup
@admin.route(
    '/help/<string:location>/<string:category>/latest',
    methods=['POST', 'GET'])
@admin.route('/help/<string:location>/latest')
@admin.route('/help/latest')
@flask_login.login_required
@requires('help')
def help_latest(location: str=None, category: str=None) -> str:
    """Automatically select next inquiry."""
    if g.queue.show_inquiry_types() and not category:
        categories = Inquiry.get_unresolved(
            str2lst(g.queue.setting('inquiry_types').value),
            location=location)
        if len(categories) > 1:
            return render_admin(
                'categories.html',
                title='Request Type',
                location=location,
                categories=categories)

    filters = {'location': location}
    if category and category != 'all':
        filters['category'] = category
    inquiry = Inquiry.current_or_latest(**filters)

    if not inquiry:
        return redirect(url_for('admin.home', notification=NOTIF_HELP_DONE))

    delayed_id = request.args.get('delayed_id', None)
    if delayed_id:
        Inquiry.query.get(delayed_id).unlock()

    inquiry.lock().link(current_user())
    return redirect(url_for(
        'admin.help_inquiry',
        id=inquiry.id,
        location=location))


# TODO: cleanup
@admin.route(
    '/help/inquiry/<string:location>/<string:id>',
    methods=['POST', 'GET'])
@admin.route('/help/inquiry/<string:id>', methods=['POST', 'GET'])
@flask_login.login_required
@requires('help')
def help_inquiry(id: str, location: str=None) -> str:
    """automatically selects next inquiry or reloads inquiry."""
    inquiry = Inquiry.query.get(id)
    if not inquiry.resolution:
        inquiry.lock()
        inquiry.link(current_user())
    if request.method == 'POST':
        delayed_id = None
        inquiry.resolution.close()

        # emit new queue positions
        emitQueuePositions(inquiry)
        emitQueueInfo(inquiry.queue)

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
            return redirect(
                url_for('admin.help_latest', delayed_id=delayed_id))
        return redirect(url_for(
            'admin.help_latest',
            location=location,
            delayed_id=delayed_id))
    return render_admin(
        'help_inquiry.html',
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

# TODO: cleanup
@admin.route('/settings', methods=['POST', 'GET'])
@flask_login.login_required
@requires('edit_settings')
def settings() -> str:
    """Show settings for the current queue."""
    settings = sorted(QueueSetting.query.join(Queue).filter_by(
        id=g.queue.id).all(), key=lambda s: s.name)
    if g.participant.role.name.lower() != 'owner':
        settings = [s for s in settings if s.name != 'whitelist']
    for setting in settings:
        if setting.name in default_queue_settings:
            # NOTE: this will filter out settings not in the default settings
            default_description = \
                default_queue_settings[setting.name]['description']
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
            setting.value = setting.value.replace(' ', '')
        setting.save()
        return redirect(url_for(
            'admin.settings',
            notification=notification))
    return render_admin('settings.html', settings=settings)


###########
# SOCKETS #
###########


@socketio.on('ping', namespace='/main')
def ping(msg: str) -> str:
    """Receive new client connection."""
    g.count = getattr(g, 'count', 0)+1
    print(' * %d pings' % g.count)
