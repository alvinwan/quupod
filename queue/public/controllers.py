from queue import db, whitelist
from queue.controllers import multi2dict
from flask import redirect, url_for
from queue.admin.models import User, Inquiry
from queue.admin.controllers import get_setting, setting
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

def add_inquiry_choices(form):
    """
    Add choices to inquiry form, based on settings

    :param InquiryForm form: form to add choices too
    :return: original form
    """
    choicify = lambda lst: [(s, s) for s in lst]
    form.location.choices = choicify(setting('Locations').split(','))
    form.category.choices = choicify(setting('Inquiry Types').split(','))
    return form

def valid_assignment(request, form):
    """
    Check if the assignment is valid, based on the settings

    :param InquiryForm form: form to check
    :return: boolean
    """
    return not get_setting(name='Assignments').enabled or \
        allowed_assignment(request, form)

def allowed_assignment(request, form):
    """
    Returns if assignment is allowed, per settings

    :param InquiryForm form: form to check
    :return: list of assignment names
    """
    lst = setting('Assignments')
    str2lst = lambda s: (s.strip() for s in lst.split(','))
    assignment, category = request.form['assignment'], request.form['category']
    if ':' in lst:
        lst = dict(lst.split(':')).get(category, None)
        if not lst:
            return True
    if assignment not in str2lst(lst):
        form.errors.setdefault('assignment', []).append('Assignment "%s" is not allowed. Only the following assignments are: %s' % (assignment, lst))
        return False
    return True

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

def present_staff():
    """Fetch all present staff members"""
    return []
