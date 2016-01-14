from queue import db, whitelist
from queue.controllers import multi2dict
from flask import redirect, url_for
from queue.admin.models import User, Inquiry
import flask_login
from queue.models import add_obj

###############
# CONTROLLERS #
###############

def add_inquiry(data):
    """
    Save inquiry

    :param Request request: Flask request object
    :return: information for confirmation page
    """
    user = flask_login.current_user
    data = multi2dict(data)
    if user.is_authenticated:
        data['owner_id'] = user.id
    add_obj(Inquiry(**data))
    return {
        'title': 'Inquiry created',
        'message': 'Inquiry created! <code>%s</code>' % str(data),
        'action': 'Back to queue',
        'url': url_for('public.home')
    }

def unresolved_inquiries():
    """
    All unresolved inquiries

    :param Request request: Flask request object
    :return: list of all inquiries
    """
    return Inquiry.query.filter_by(status='unresolved').all()

def resolving_inquiries():
    """
    All inquiries currently being resolved

    :param Request request: Flask request object
    :return: list of all inquiries
    """
    return Inquiry.query.filter_by(status='resolving').all()

def add_user(data):
    """
    Save user

    :param Request request: Flask request object
    :return: information for confirmation page
    """
    data = multi2dict(data)
    whitelist_promote(User(**data))
    return {
        'message': 'Signed up! <code>%s</code>' % str({
            'username': data['username'],
            'email': data['email'],
            'name': data['name']
        }),
        'action': 'Sign in',
        'url': url_for('public.login')
    }

def get_user(**kwargs):
    """
    Get user by kwargs.

    :param kwargs: key arguments containing user details
    :return: User object or None
    """
    return User.query.filter_by(**kwargs).first()

def get_user_home(user):
    """
    Get home page for user

    :param User user: user object
    :return: User object or None
    """
    if user and getattr(user, 'role', None) == 'admin':
        return redirect(url_for('admin.home'))
    return redirect(url_for('public.home'))

def whitelist_promote(user):
    """
    Promote a user if on the whitelist

    :param User user: user object
    :return: origina User object
    """
    if user.email in whitelist:
        user.role = 'staff'
    return add_obj(user)
