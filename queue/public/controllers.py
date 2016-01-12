from queue import db
from flask import redirect, url_for
from queue.staff.models import User, Inquiry, add_obj

###############
# CONTROLLERS #
###############

def add_inquiry(data):
    """
    Save inquiry

    :param Request request: Flask request object
    :return: information for confirmation page
    """
    add_obj(Inquiry(**data))
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
    add_obj(User(**data))
    return {
        'message': 'Signed up! <code>%s</code>' % str(data),
        'action': 'Sign in',
        'url': url_for('public.signin')
    }
