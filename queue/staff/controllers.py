from flask import url_for
from queue import db
from .models import Inquiry, add_obj
from sqlalchemy import desc


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
        'action': 'staff home',
        'url': url_for('staff.home')
    }

def get_inquiry(id):
    """
    Retrieve inquiry, or retrieve latest inquiry.

    :param id: id of inquiry or None
    :return: Inquiry object
    """
    return Inquiry.query.filter_by(id=id).first()

def get_latest_inquiry():
    """
    Retrieve latest unresolved inquiry.

    :param id: id of Inquiry
    :return: Inquiry object
    """
    return Inquiry.query.filter_by(status='unresolved').order_by(
        desc(Inquiry.created_at)).first()

def lock_inquiry(inquiry):
    """
    Lock inquiry as 'resolving' so no other staff member takes it.

    :param Inquiry inquiry: Inquiry object
    :return: original inquiry object
    """
    if not inquiry:
        return None
    inquiry.status = 'resolving'
    add_obj(inquiry)
    return inquiry

def resolve_inquiry(inquiry):
    """
    Mark inquiry as 'resolved'.

    :param Inquiry inquiry: Inquiry object
    :return: original inquiry object
    """
    if not inquiry:
        return None
    inquiry.status = 'resolved'
    add_obj(inquiry)
    return inquiry
