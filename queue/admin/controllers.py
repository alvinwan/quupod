from flask import url_for
from queue import db
from queue.controllers import multi2dict
from queue.models import add_obj, Setting
from .models import Inquiry, Resolution
from sqlalchemy import asc
import flask_login, arrow


#############
# INQUIRIES #
#############

def clear_unfinished():
    """
    Clear all unfinished inquiries, which includes unresolved and inquiries
    current being resolved.
    """
    Inquiry.query.filter_by(status='unresolved').update({'status': 'closed'})
    Inquiry.query.filter_by(status='resolving').update({'status': 'closed'})
    db.session.commit()
    return {
        'message': 'All cleared',
        'action': 'admin home',
        'url': url_for('admin.home')
    }

def get_inquiry(id):
    """
    Retrieve inquiry, or retrieve latest inquiry.

    :param id: id of inquiry or None
    :return: Inquiry object
    """
    return Inquiry.query.filter_by(id=id).first()

def get_inquiries(f='all', **kwargs):
    """
    Retrieve inquiries

    :param kwargs: filters
    :return: Inquiry object
    """
    return getattr(Inquiry.query.filter_by(**kwargs), f)()

def get_current_inquiry():
    """
    Return current inquiry if exists.

    :return: Inquiry
    """
    user = flask_login.current_user
    resolution = Resolution.query.filter_by(user_id=user.id, resolved_at=None).first()
    if resolution:
        return resolution.inquiry

def get_latest_inquiry(offset=0, **kwargs):
    """
    Retrieve latest unresolved inquiry. If there is a current inquiry the
    current staff member is resolving, that inquiry will be loaded instead.

    :param kwargs: keyword arguments to filter by
    :return: Inquiry object
    """
    user, current_inquiry = flask_login.current_user, get_current_inquiry()
    if current_inquiry:
        return current_inquiry
    kwargs = {k:v for k, v in kwargs.items() if v}
    return Inquiry.query.filter_by(status='unresolved', **kwargs).order_by(
        asc(Inquiry.created_at)).offset(offset).first()

def lock_inquiry(inquiry):
    """
    Lock inquiry as 'resolving' so no other admin member takes it.

    :param Inquiry inquiry: Inquiry object
    :return: original inquiry object
    """
    if not inquiry:
        return None
    inquiry.status = 'resolving'
    return add_obj(inquiry)

def link_inquiry(inquiry):
    """
    Link inquiry with current staff member.

    :param Inquiry inquiry: Inquiry object
    :return: new Resolution object
    """
    user = flask_login.current_user
    resolution = Resolution.query.filter_by(
        user_id=user.id, inquiry_id=inquiry.id, resolved_at=None).first()
    if not resolution:
        return add_obj(Resolution(user_id=user.id, inquiry_id=inquiry.id))
    return resolution

def close_inquiry(inquiry, status='resolved'):
    """
    Mark inquiry as 'resolved'.

    :param Inquiry inquiry: Inquiry object
    :return: original inquiry object
    """
    user = flask_login.current_user
    if not inquiry:
        return None
    inquiry.status = status
    if inquiry.resolution:
        close_resolution(inquiry)
    return add_obj(inquiry)

def close_resolution(inquiry):
    """
    Close resolution.

    :param Inquiry inquiry: Inquiry object
    :return: resolution object
    """
    user = flask_login.current_user
    resolution = Resolution.query.filter_by(
        user_id=user.id, inquiry_id=inquiry.id, resolved_at=None).first()
    resolution.resolved_at = arrow.utcnow()
    return add_obj(resolution)


############
# SETTINGS #
############

def get_settings(**kwargs):
    """
    Get settings by filters

    :param kwargs: keyword argument filters
    :return: list of Setting objects
    """
    return Setting.query.filter_by(**kwargs).all()


def get_setting(**kwargs):
    """
    Get setting by filters

    :param kwargs: keyword argument filters
    :return: Setting object
    """
    return Setting.query.filter_by(**kwargs).first()


def setting(name):
    """Return setting value"""
    try:
        return get_setting(name=name).value
    except AttributeError:
        return None
