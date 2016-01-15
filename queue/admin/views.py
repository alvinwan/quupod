from flask import Blueprint, request, redirect, url_for
from queue import app
from queue.views import requires, render
from queue.public.controllers import unresolved_inquiries, resolving_inquiries
from .models import User, Inquiry
from queue.notifications import *
from .controllers import *
import flask_login


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
    if not get_setting(name='Location Selection').enabled:
        return redirect(url_for('admin.help_latest'))
    locations = [(l, len(list(get_inquiries(location=l, status='unresolved'))))
        for l in setting('Locations').split(',')]
    return render('help.html',
        no_mobile_action=True,
        locations=[t for t in locations if t[1]])

@admin.route('/clear/<string:location>', methods=['POST', 'GET'])
@admin.route('/clear', methods=['POST', 'GET'])
@flask_login.login_required
@requires('staff')
def clear(location=None):
    """Clear all inquiries, period. Or, clear all inquiries for a location."""
    if location:
        return 'Not yet implemented.'
    if request.method == 'POST':
        return render('admin_confirm.html', **clear_unfinished())
    return render('admin_confirm.html',
        message='Are you sure? This will clear all resolving and unresolved. \
        <form method="POST"><input type="submit" value="clear"></form>',
        action='admin home',
        url=url_for('admin.home'))

@admin.route('/help/<string:location>/latest')
@admin.route('/help/latest')
@flask_login.login_required
@requires('staff')
def help_latest(location=None):
    """automatically selects next inquiry"""
    inquiry = get_latest_inquiry(location=location)
    if not inquiry:
        return redirect(url_for('admin.help', notification=NOTIF_HELP_DONE))
    lock_inquiry(inquiry)
    return redirect(url_for('admin.help_inquiry',
        id=inquiry.id, location=location))

@admin.route('/help/<string:location>/<string:id>', methods=['POST', 'GET'])
@admin.route('/help/<string:id>', methods=['POST', 'GET'])
@flask_login.login_required
@requires('staff')
def help_inquiry(id, location=None):
    """automatically selects next inquiry or reloads inquiry """
    inquiry = get_inquiry(id)
    link_inquiry(inquiry)
    if request.method == 'POST':
        resolve_inquiry(inquiry)
        if not location:
            return redirect(url_for('admin.help_latest'))
        return redirect(url_for('admin.help_latest', location=location))
    return render('help_inquiry.html', inquiry=inquiry)


############
# SETTINGS #
############

@admin.route('/settings', methods=['POST', 'GET'])
@flask_login.login_required
@requires('staff')
def settings():
    """settings"""
    settings = get_settings()
    if request.method == 'POST':
        notification = NOTIF_SETTING_UPDATED
        setting = Setting.query.filter_by(name=request.form['name']).first()
        for k, v in request.form.items():
            setattr(setting, k, v)
        if (request.form['name'] == 'Google Login' and request.form['enabled'] == '0' and not get_setting(name='Default Login').enabled) or (
            request.form['name'] == 'Default Login' and request.form['enabled'] == '0' and not get_setting(name='Google Login').enabled):
            return redirect(url_for('admin.settings',notification=ERR_NO_LOGIN))
        if setting.name == 'Inquiry Types' and len(setting.value.split(',')) == 1:
            notification = NOTIF_SETTING_ONE_TYPE
        setting = add_obj(setting)
        return redirect(url_for('admin.settings',
            notification=notification))
    return render('settings.html', settings=settings)
