from flask import Blueprint, request, redirect, url_for
from quuupod import app
from quuupod.views import requires, render
from quuupod.public.controllers import unresolved_inquiries, resolving_inquiries
from .models import User, Inquiry
from quuupod.notifications import *
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
    locations = [(l, get_inquiries('count', location=l, status='unresolved'))
        for l in setting('Locations').split(',')]
    return render('help.html',
        no_mobile_action=True,
        locations=[t for t in locations if t[1]],
        current_inquiry=get_current_inquiry())

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

@admin.route('/help/<string:location>/<string:category>/latest', methods=['POST', 'GET'])
@admin.route('/help/<string:location>/latest')
@admin.route('/help/latest')
@flask_login.login_required
@requires('staff')
def help_latest(location=None, category=None):
    """automatically selects next inquiry"""
    inquiry = get_latest_inquiry(location=location, category=category)
    if not inquiry:
        return redirect(url_for('admin.help', notification=NOTIF_HELP_DONE))
    if get_setting(name='Inquiry Types').enabled and not category:
        categories = [(cat, get_inquiries('count',
            category=cat, status='unresolved', location=location))
            for cat in setting('Inquiry Types').split(',')]
        categories = [c for c in categories if c[1]]
        if len(categories) > 1:
            return render('categories.html',
                title='Request Type',
                location=location,
                categories=categories)
    delayed_id = request.args.get('delayed_id', None)
    if delayed_id:
        close_inquiry(get_inquiry(delayed_id), status='unresolved')
    lock_inquiry(inquiry)
    link_inquiry(inquiry)
    return redirect(url_for('admin.help_inquiry',
        id=inquiry.id, location=location))

@admin.route('/help/inquiry/<string:location>/<string:id>', methods=['POST', 'GET'])
@admin.route('/help/inquiry/<string:id>', methods=['POST', 'GET'])
@flask_login.login_required
@requires('staff')
def help_inquiry(id, location=None):
    """automatically selects next inquiry or reloads inquiry """
    inquiry = get_inquiry(id)
    if request.method == 'POST':
        delayed_id=None
        if request.form['status'] == 'unresolved':
            delayed_id = inquiry.id
            close_resolution(inquiry)
        else:
            close_inquiry(inquiry)
        if not location:
            return redirect(url_for('admin.help_latest', delayed_id=delayed_id))
        return redirect(url_for('admin.help_latest',
            location=location, delayed_id=delayed_id))
    return render('help_inquiry.html',
        inquiry=inquiry,
        inquiries=get_inquiries(name=inquiry.name, limit=10),
        hide_event_nav=True)


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
