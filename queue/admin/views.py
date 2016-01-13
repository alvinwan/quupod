from flask import Blueprint, render_template, request, redirect, url_for
from queue import app
from queue.views import requires
from queue.public.controllers import unresolved_inquiries, resolving_inquiries
from .models import User, Inquiry
from .controllers import *
from .forms import *
import flask_login


admin = Blueprint('admin', __name__, url_prefix='/admin')

#########
# ADMIN #
#########

@admin.route('/')
@flask_login.login_required
@requires('staff')
def home():
    """admin homepage"""
    events = get_events()
    return render_template('admin.html', events=events)

@requires('staff')
@admin.route('/clear/<string:location>', methods=['POST', 'GET'])
@admin.route('/clear', methods=['POST', 'GET'])
def clear(location=None):
    """Clear all inquiries, period. Or, clear all inquiries for a location."""
    if location:
        return 'Not yet implemented.'
    if request.method == 'POST':
        return render_template('confirm.html', **clear_unfinished())
    return render_template('confirm.html',
        message='Are you sure? This will clear all resolving and unresolved. \
        <form method="POST"><input type="submit" value="clear"></form>',
        action='admin home',
        url=url_for('admin.home'))

@requires('staff')
@admin.route('/help')
def help():
    """automatically selects next inquiry"""
    inquiry = get_latest_inquiry()
    if not inquiry:
        return render_template('confirm.html',
            title='All done!',
            message='No more inquiries to process!',
            url=url_for('admin.home'),
            action='admin home')
    lock_inquiry(inquiry)
    return redirect(url_for('admin.help_inquiry', id=inquiry.id))

@requires('staff')
@admin.route('/help/<string:id>', methods=['POST', 'GET'])
def help_inquiry(id):
    """automatically selects next inquiry or reloads inquiry """
    inquiry = get_inquiry(id)
    if request.method == 'POST':
        resolve_inquiry(inquiry)
        return redirect(url_for('admin.help'))
    return render_template('help.html', inquiry=inquiry)


#########
# EVENT #
#########

# datetime format %Y-%m-%d %H:%M:%S format: 2016-1-13 12:00:00

@requires('staff')
@admin.route('/event/create', methods=['POST', 'GET'])
def event_create():
    """create a new event"""
    form = EventForm(request.form)
    if request.method == 'POST' and form.validate():
        event = create_event(request.form)
        return redirect(url_for('admin.event_detail', id=event.id))
    return render_template('form.html', form=form, title='Create Event')

@requires('/admin')
@admin.route('/event/<string:id>/edit', methods=['POST', 'GET'])
def event_edit(id):
    event = get_event(id=id)
    form = EventForm(request.form, obj=event)
    if request.method == 'POST' and form.validate():
        event = edit_event(event, request.form)
        return redirect(url_for('admin.event_detail', id=event.id))
    return render_template('form.html', form=form, title='Edit Event')

@requires('/admin')
@admin.route('/event/<string:id>', methods=['POST', 'GET'])
def event_detail(id):
    event = get_event(id=id)
    return render_template('event_detail.html', event=event)


#############
# ANALYTICS #
#############

@requires('staff')
@admin.route('/analytics')
def analytics():
    """analytics for requests"""
    return render_template('analytics.html')
