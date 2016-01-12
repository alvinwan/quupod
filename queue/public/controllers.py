from queue import db
from flask import redirect, url_for
from queue.staff.models import User, Inquiry, add_obj

#############
# UTILITIES #
#############

def multi2dict(multi):
    return dict(multi.items())

###############
# CONTROLLERS #
###############

def add_inquiry(data):
    """
    Save inquiry

    :param Request request: Flask request object
    :return: information for confirmation page
    """
    add_obj(Inquiry(**multi2dict(data)))
    return {
        'message': 'Inquiry created! <code>%s</code>' % str(data),
        'action': 'Back to queue',
        'url': url_for('public.queue')
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
    add_obj(User(**multi2dict(data)))
    return {
        'message': 'Signed up! <code>%s</code>' % str({
            'username': data['username'],
            'email': data['email'],
            'name': data['name']
        }),
        'action': 'Sign in',
        'url': url_for('public.signin')
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
    if user and getattr(user, 'role', None) == 'staff':
        return redirect(url_for('staff.home'))
    return redirect(url_for('public.queue'))
