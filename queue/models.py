"""
Important: Changes here need to be followed by `make refresh`.
"""

from queue import db
from sqlalchemy import types
from sqlalchemy_utils import ArrowType
import flask_login, arrow

#############
# UTILITIES #
#############

def add_obj(obj):
    """
    Add object to database

    :param obj: any instance of a Model
    :return: information regarding database add
    """
    try:
        db.session.add(obj)
        db.session.commit()
        return obj
    except:
        db.session.rollback()
        add_obj(obj)

##########
# MODELS #
##########

class Setting(db.Model):
    """settings for the queue application"""

    __tablename__ = 'setting'
    id = db.Column(db.Integer, primary_key=True)
    updated_at = db.Column(ArrowType)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(ArrowType, default=arrow.utcnow())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    name = db.Column(db.String(50), unique=True)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    toggable = db.Column(db.Boolean, default=False)
    enabled = db.Column(db.Boolean, default=True)
    enable_description = db.Column(db.Text)
    input_type = db.Column(db.String(20), default='text')
