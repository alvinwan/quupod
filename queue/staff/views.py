from flask import Blueprint, render_template, request, redirect, url_for
from queue import app
from .models import User, Inquiry
from .controllers import *


staff = Blueprint('staff', __name__, url_prefix='/staff')

#########
# ADMIN #
#########

@staff.route('/')
def home():
    """staff homepage"""
    # option to see analytics or to start helping
    return render_template('staff.html')

@staff.route('/help/<string:id>', methods=['POST', 'GET'])
@staff.route('/help')
def help(id=None):
    """automatically selects next inquiry or reloads inquiry """
    if not id:
        inquiry = get_latest_inquiry()
        lock_inquiry(inquiry)
        return redirect(url_for('staff.help', id=inquiry.id))
    inquiry = get_inquiry(id)
    if request.method == 'POST':
        resolve_inquiry(inquiry)
        return redirect(url_for('staff.help'))
    return render_template('help.html', inquiry=inquiry)

#############
# ANALYTICS #
#############

@staff.route('/analytics')
def analytics():
    """analytics for requests"""
    return render_template('analytics.html')
