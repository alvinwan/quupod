from flask import Blueprint, request, redirect, url_for
from queue import app
from queue.views import requires, render
from queue.public.controllers import unresolved_inquiries, resolving_inquiries
from .models import User, Inquiry
from .controllers import *
import flask_login
from default_settings import load_settings


admin = Blueprint('admin', __name__, url_prefix='/admin',
    template_folder='templates')

#########
# ADMIN #
#########

@admin.route('/')
@flask_login.login_required
@requires('staff')
def home():
    """admin homepage"""
    return render('home.html')

@admin.route('/help')
@flask_login.login_required
@requires('staff')
def help():
    """help start"""
    return render('help.html')

@admin.route('/clear/<string:location>', methods=['POST', 'GET'])
@admin.route('/clear', methods=['POST', 'GET'])
@flask_login.login_required
@requires('staff')
def clear(location=None):
    """Clear all inquiries, period. Or, clear all inquiries for a location."""
    if location:
        return 'Not yet implemented.'
    if request.method == 'POST':
        return render('confirm.html', **clear_unfinished())
    return render('confirm.html',
        message='Are you sure? This will clear all resolving and unresolved. \
        <form method="POST"><input type="submit" value="clear"></form>',
        action='admin home',
        url=url_for('admin.home'))

@admin.route('/help/<string:location>')
@flask_login.login_required
@requires('staff')
def help_location(location):
    """automatically selects next inquiry"""
    inquiry = get_latest_inquiry(location=location)
    if not inquiry:
        return render('confirm.html',
            title='All done!',
            message='No more inquiries to process!',
            url=url_for('admin.home'),
            action='admin home')
    lock_inquiry(inquiry)
    return redirect(url_for('admin.help_inquiry', id=inquiry.id))

@admin.route('/help/<string:location>/<string:id>', methods=['POST', 'GET'])
@admin.route('/help/<string:id>', methods=['POST', 'GET'])
@flask_login.login_required
@requires('staff')
def help_inquiry(id, location=None):
    """automatically selects next inquiry or reloads inquiry """
    inquiry = get_inquiry(id)
    if request.method == 'POST':
        resolve_inquiry(inquiry)
        return redirect(url_for('admin.help_location', location=location))
    return render('help_inquiry.html', inquiry=inquiry)


############
# SETTINGS #
############

@admin.route('/settings', methods=['POST', 'GET'])
@flask_login.login_required
@requires('staff')
def settings():
    """settings"""
    load_settings()
    settings = get_settings()
    if request.method == 'POST':
        setting = Setting.query.filter_by(name=request.form['name']).first()
        for k, v in request.form.items():
            setattr(setting, k, v)
        setting = add_obj(setting)
        return redirect(url_for('admin.settings'))
    return render('settings.html', settings=settings)
