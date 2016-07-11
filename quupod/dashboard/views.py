"""The dashboard contains a list of all queues the user is involved with."""

from flask import Blueprint, request, redirect
from quupod.views import current_user, url_for
from quupod.queue.forms import QueueForm
from quupod.models import Queue
from quupod.defaults import default_queue_roles
import flask_login


dashboard = Blueprint(
    'dashboard',
    __name__,
    url_prefix='/dashboard', template_folder='templates')


def render_dashboard(f, *args, **kwargs):
    """Custom render for dashboard."""
    from quupod.views import render
    return render(f, *args, **kwargs)


#############
# DASHBOARD #
#############


@dashboard.route('/')
@flask_login.login_required
def home():
    """User dashboard, contains all involved queues."""
    return render_dashboard(
        'dashboard/index.html', queues=current_user().queues(),
        empty='You aren\'t participating in any queues!')


@dashboard.route('/q/', methods=['GET', 'POST'])
@flask_login.login_required
def create_queue():
    """The 'Create queue' form."""
    form = QueueForm(request.form)
    if request.method == 'POST' and form.validate():
        queue = Queue.from_request().save().load_roles(
            default_queue_roles[request.form['category']]).save()
        current_user().join(queue, role='Owner')
        queue.load_settings('whitelist')
        return redirect(url_for('queue.home', queue_url=queue.url))
    return render_dashboard(
        'form_public.html',
        title='Create Queue',
        submit='create',
        form=form)
