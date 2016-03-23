from . import socketio
from quupod.models import Inquiry

@socketio.on('resolve', namespace='/main')
def resolve(inquiry_id):
    """
    Invoked whenever a request is marked as resolved.

    :param int inquiry_id: ID for the inquiry resolved
    """
    emit('update position',
        {'positions': ''},
        broadcast=True)
