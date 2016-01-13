from flask import url_for
from queue import db
from queue.controllers import multi2dict
from .models import Inquiry, add_obj, Assignment, Problem
from sqlalchemy import desc


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


###############
# ASSIGNMENTS #
###############

def create_assignment(data):
    """
    Create a new assignment for the queue

    :param ImmutableDict data: all data for Assignment
    :return: new Assignment object
    """
    data = multi2dict(data)
    data['is_active'] = True if data.get('is_active', None) == 'y' else False
    return add_obj(Assignment(**data))


def get_assignment(**kwargs):
    """
    Get assignment by keyword argument filters.

    :param kwargs: key arguments
    :return: Assignment object
    """
    return Assignment.query.filter_by(**kwargs).first()


def get_assignments(**kwargs):
    """
    Get all assignments that match the filters

    :param kwargs: keyword argument filters
    :return: list of Problem objects
    """
    return Assignment.query.filter_by(**kwargs).all()


def create_problem(assignmentId, data):
    """
    Create a new problem

    :param ImmutableDict data: all data for a problem
    :return: new Problem object
    """
    data = multi2dict(data)
    data['assignment_id'] = assignmentId
    return add_obj(Problem(**data))


def get_problem(**kwargs):
    """
    Get problem according to filters.

    :param kwargs: keyword argument filters
    :return: Problem
    """
    return Problem.query.filter_by(**kwargs).first()


def get_problems(**kwargs):
    """
    Get all problems that match the filters

    :param kwargs: keyword argument filters
    :return: list of Problem objects
    """
    return Problem.query.filter_by(**kwargs).all()


def edit_problem(problem, data):
    """
    Update a problem using data.

    :param ImmutableDict data: data
    :param Problem problem: problem object to update
    :return: old problem object
    """
    for k, v in data.items():
        setattr(problem, k, v)
    return add_obj(problem)
