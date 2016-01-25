from flask import Blueprint, request, redirect, url_for, g
from quuupod.views import current_user, login_required
from quuupod.queue.forms import QueueForm
from quuupod.models import Queue
from quuupod.defaults import default_queue_roles


dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard.url_value_preprocessor
def load_current_user(_, __):
    g.user = current_user()


def render_dashboard(f, *args, **kwargs):
    """custom render for dashboard"""
    from quuupod.views import render
    return render(f, *args, **kwargs)


#############
# DASHBOARD #
#############


@dashboard.route('/')
@login_required
def home():
    """user dashboard"""
    return render_dashboard('dashboard/index.html', queues=g.user.queues(),
        empty='You aren\'t participating in any queues!')


@dashboard.route('/q/', methods=['GET', 'POST'])
@login_required
def create_queue():
    """create queue form"""
    form = QueueForm(request.form)
    if request.method == 'POST' and form.validate():
        queue = Queue.from_request().save().load_roles(
            default_queue_roles[request.form['category']]).save()
        g.user.join(queue, role='Owner')
        queue.load_settings('whitelist')
        return redirect(url_for('queue.home', queue_url=queue.url))
    return render_dashboard('form_public.html',
        title='Create Queue',
        submit='create',
        form=form)
