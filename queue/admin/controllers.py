from flask import url_for
from queue import db
from queue.controllers import multi2dict
from .models import Inquiry, add_obj, Assignment
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
        desc(Inquiry.created_at)).first()

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


def get_problems(assignment):
    """
    Get all problems that match the filters

    :param kwargs: keyword argument filters
    :return: list of Problem objects
    """
    return [{'name': n, 'count': len(get_problem_inquiries(assignment.id, n))}
        for n in assignment.problems.split(',')]


def get_problem_inquiries(assignmentId, problem):
    """
    Get all inquiries for a problem

    :param int assignmentId: assignment id
    :param str problem: problem number
    :return: list of Inquiries
    """
    return Inquiry.query.filter_by(
        assignment_id=assignmentId, problem=problem).all()
