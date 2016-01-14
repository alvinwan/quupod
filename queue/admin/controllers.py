from flask import url_for
from queue import db
from queue.controllers import multi2dict
from queue.models import add_obj, Setting
from .models import Inquiry
from sqlalchemy import asc


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

def get_latest_inquiry(**kwargs):
    """
    Retrieve latest unresolved inquiry.

    :param kwargs: keyword arguments to filter by
    :return: Inquiry object
    """
    return Inquiry.query.filter_by(status='unresolved', **kwargs).order_by(
        asc(Inquiry.created_at)).first()

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

def resolve_inquiry(inquiry):
    """
    Mark inquiry as 'resolved'.

    :param Inquiry inquiry: Inquiry object
    :return: original inquiry object
    """
    if not inquiry:
        return None
    inquiry.status = 'resolved'
    return add_obj(inquiry)


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
