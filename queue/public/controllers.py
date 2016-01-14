from queue import db, whitelist
from queue.controllers import multi2dict
from flask import redirect, url_for
from queue.admin.models import User, Inquiry, Resolution
from queue.admin.controllers import get_setting, setting
import flask_login, arrow
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
        lst = dict(l.split(':') for l in lst.splitlines()).get(category, '*')
        if lst == '*':
            return True
    if assignment not in str2lst(lst):
        form.errors.setdefault('assignment', []).append('For "%s" inquiries, assignment "%s" is not allowed. Only the following assignments are: %s' % (category, assignment, lst))
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

def login_and_redirect(user):
    """
    Login and redirect user

    :param User user: user object
    :return: redirect
    """
    flask_login.login_user(user)
    whitelist_promote(user)
    print(' * %s (%s) logged in.' % (user.name, user.email))
    return get_user_home(user)

def present_staff():
    """Fetch all present staff members"""
    resolutions = Resolution.query.filter(
        Resolution.resolved_at >= arrow.utcnow().replace(hours=-3)).all()
    staff = set()
    for resolution in resolutions:
        user = get_user(id=resolution.user_id)
        user.resolution = resolution
        ns = [res.resolved_at - res.created_at for res in Resolution.query.filter(
            Resolution.resolved_at >= arrow.utcnow().replace(hours=-6),
            Resolution.user_id == user.id
        )]
        if ns:
            total = ns[0]
            for n in ns[1:]:
                total = n + total
            user.average = total/len(ns)
        else:
            user.average = 'n/a'
        current = Resolution.query.filter_by(user_id=user.id,
            resolved_at=None).first()
        user.status = 'free' if not current else 'busy'
        staff.add(user)
    return staff


def ttr():
    """Compute average time until resolution."""
    resolutions = Resolution.query.filter(
        Resolution.resolved_at >= arrow.utcnow().replace(hours=-3)).all()
    ns = [res.resolved_at - res.created_at for res in resolutions]
    if ns:
        total = ns[0]
        for n in ns[1:]:
            total = n + total
        return total/len(ns)
    return 'n/a'


def verify_google_token(token):
    """
    Verify a google token

    :param token str: token
    :return: token information if valid or None
    """
    from oauth2client import client, crypt

    try:
        idinfo = client.verify_id_token(token, CLIENT_ID)
        # If multiple clients access the backend server:
        if idinfo['aud'] not in [ANDROID_CLIENT_ID, IOS_CLIENT_ID, WEB_CLIENT_ID]:
            raise crypt.AppIdentityError("Unrecognized client.")
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")
        if idinfo['hd'] != APPS_DOMAIN_NAME:
            raise crypt.AppIdentityError("Wrong hosted domain.")
    except crypt.AppIdentityError:
        return
    return idinfo
