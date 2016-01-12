from flask import Blueprint, render_template, request, redirect, url_for
from queue import app
from queue.views import requires
from queue.public.controllers import unresolved_inquiries, resolving_inquiries
from .models import User, Inquiry
from .controllers import *
import flask_login


staff = Blueprint('staff', __name__, url_prefix='/staff')

#########
# ADMIN #
#########

@staff.route('/')
@flask_login.login_required
@requires('staff')
def home():
    """staff homepage"""
    # option to see analytics or to start helping
    return render_template('staff.html')

@requires('staff')
@staff.route('/clear/<string:location>', methods=['POST', 'GET'])
@staff.route('/clear', methods=['POST', 'GET'])
def clear(location=None):
    """Clear all inquiries, period. Or, clear all inquiries for a location."""
    if location:
        return 'Not yet implemented.'
    if request.method == 'POST':
        return render_template('confirm.html', **clear_unfinished())
    return render_template('confirm.html',
        message='Are you sure? This will clear all resolving and unresolved. \
        <form method="POST"><input type="submit" value="clear"></form>',
        action='staff home',
        url=url_for('staff.home'))

@requires('staff')
@staff.route('/help')
def help():
    """automatically selects next inquiry"""
    inquiry = get_latest_inquiry()
    if not inquiry:
        return render_template('confirm.html',
            message='No more inquiries to process!',
            url=url_for('staff.home'),
            action='staff home')
    lock_inquiry(inquiry)
    return redirect(url_for('staff.help_inquiry', id=inquiry.id))

@requires('staff')
@staff.route('/help/<string:id>', methods=['POST', 'GET'])
def help_inquiry(id):
    """automatically selects next inquiry or reloads inquiry """
    inquiry = get_inquiry(id)
    if request.method == 'POST':
        resolve_inquiry(inquiry)
        return redirect(url_for('staff.help'))
    return render_template('help.html', inquiry=inquiry)

#############
# ANALYTICS #
#############

@requires('staff')
@staff.route('/analytics')
def analytics():
    """analytics for requests"""
    return render_template('analytics.html')
