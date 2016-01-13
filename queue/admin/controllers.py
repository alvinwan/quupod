from flask import url_for
from queue import db
from queue.controllers import multi2dict
from .models import Inquiry, add_obj, Event
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

def get_latest_inquiry():
    """
    Retrieve latest unresolved inquiry.

    :param id: id of Inquiry
    :return: Inquiry object
    """
    return Inquiry.query.filter_by(status='unresolved').order_by(
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


##########
# EVENTS #
##########

def create_event(data):
    """
    Create a new event for the queue

    :param ImmutableDict data: all data for event
    :return: new Event object
    """
    return add_obj(Event(**multi2dict(data)))

def get_event(**kwargs):
    """
    Retrieve event

    :param kwargs: key argument filters
    :return: Event object
    """
    return Event.query.filter_by(**kwargs).first()

def get_events(**kwargs):
    """
    Retrieve events

    :param kwargs: key argument filters
    :return: list of Event objects
    """
    return Event.query.filter_by(**kwargs).all()
