from flask import redirect, url_for
from queue.staff.models import User, Inquiry

#############
# UTILITIES #
#############

def add_obj(obj):
    """
    Add object to database

    :param obj: any instance of a Model
    :return: information regarding database add
    """
    db.session.add(obj)
    db.session.commit()

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
    return {'data': data}

def queued_inquiries(request):
    """
    All queued inquiries

    :param Request request: Flask request object
    :return: list of all inquiries
    """
    return Inquiry.query.filter_by(status='unresolved').all()

def add_user(data):
    """
    Save user

    :param Request request: Flask request object
    :return: information for confirmation page
    """
    add_obj(User(**data))
    return {'data': data}
