"""Views for the queue admin panel."""

from flask import Blueprint
from flask import request
from flask import redirect
from flask import g
from flask import abort
from quupod import socketio
from quupod.views import requires
from quupod.views import url_for
from quupod.views import current_user
from quupod.models import Inquiry
from quupod.models import Queue
from quupod.models import Participant
from quupod.notifications import NOTIF_HELP_DONE
from quupod.notifications import NOTIF_SETTING_UPDATED
from quupod.notifications import NOTIF_SETTING_ONE_TYPE
from quupod.queue.views import render_queue
from quupod.utils import emitQueuePositions
from quupod.utils import emitQueueInfo
from quupod.utils import str2lst
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


def render_admin(template: str, *args, **context) -> str:
    """Special rendering for queue admin."""
    return render_queue(template, *args, **context)


#########
# ADMIN #
#########

@admin.route('/')
@flask_login.login_required
@requires('help')
def home() -> str:
    """The queue administration home page."""
    return render_admin(
        'home.html',
        num_inquiries=Inquiry.get_num_unresolved(),
        latest_inquiry=Inquiry.get_current_or_latest(),
        current_inquiry=Inquiry.get_current(),
        ttr=g.queue.ttr(),
        earliest_request=Inquiry.get_earliest(),
        locations=Inquiry.get_unresolved(
            str2lst(g.queue.setting('locations').value), 'location'))

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
        categories = Inquiry.get_categories_unresolved(location=location)
        if len(categories) > 1:
            return render_admin(
                'categories.html',
                title='Request Type',
                location=location,
                categories=categories)
    inquiry = Inquiry.get_current_or_latest(
        location=location,
        category=category)
    Inquiry.maybe_unlock_delayed()
    if not inquiry:
        return redirect(url_for('admin.home', notification=NOTIF_HELP_DONE))
    inquiry.lock().link(current_user())
    return redirect(url_for(
        'admin.help_inquiry',
        id=inquiry.id,
        location=location))


@admin.route(
    '/help/inquiry/<string:location>/<string:id>',
    methods=['POST', 'GET'])
@admin.route('/help/inquiry/<string:id>', methods=['POST', 'GET'])
@flask_login.login_required
@requires('help')
def help_inquiry(id: str, location: str=None) -> str:
    """automatically selects next inquiry or reloads inquiry."""
    inquiry = Inquiry.query.get(id).maybe_lock()
    if request.method == 'POST':
        delayed_id = None
        inquiry.resolution.close()
        emitQueuePositions(inquiry)
        emitQueueInfo(inquiry.queue)
        if request.form['status'] == 'resolved':
            inquiry.resolved()
        elif request.form['status'] == 'unresolved':
            delayed_id = id
        if request.form['load_next'] != 'y':
            if request.form['status'] == 'unresolved':
                inquiry.unlock()
            return redirect(url_for('admin.home'))
        return redirect(
            url_for(
                'admin.help_latest',
                location=location,
                delayed_id=delayed_id))
    return render_admin(
        'help_inquiry.html',
        inquiry=inquiry,
        inquiries=Inquiry.get_current_user_inquiries(),
        hide_event_nav=True,
        group=inquiry.get_similar_inquiries(),
        wait_time=inquiry.get_wait_time('%h:%m:%s'))


############
# SETTINGS #
############

@admin.route('/settings', methods=['POST', 'GET'])
@flask_login.login_required
@requires('edit_settings')
def settings() -> str:
    """Show settings for the current queue."""
    if request.method == 'POST':
        notification = NOTIF_SETTING_UPDATED
        setting = (
            g.queue
            .setting(request.form['name'])
            .update(**dict(request.form.items())))
        # TODO convert all settings into objects, with permissions check and
        # post processing
        if setting.name == 'locations':
            setting.value = setting.value.replace(' ', '')
        if setting.name == 'inquiry_types' and \
                len(str2lst(setting.value)) == 1 and \
                bool(int(setting.enabled)) is True:
            notification = NOTIF_SETTING_ONE_TYPE
        setting.save()
        return redirect(url_for(
            'admin.settings',
            notification=notification))
    return render_admin('settings.html', settings=g.queue.cleaned_settings)


###########
# SOCKETS #
###########


@socketio.on('ping', namespace='/main')
def ping(msg: str) -> str:
    """Receive new client connection."""
    g.count = getattr(g, 'count', 0)+1
    print(' * %d pings' % g.count)
