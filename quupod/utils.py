from string import Template
from flask_socketio import emit, disconnect
from sqlalchemy import asc
import json

class DeltaTemplate(Template):
    delimiter = "%"

def strfdelta(tdelta, fmt='%h:%m:%s'):
    """
    Formats timedeltas
    http://stackoverflow.com/a/8907269/4855984

    >>> strfdelta(delta_obj, "%D days %H:%M:%S")
    1 days 2:8:2
    >>> strfdelta(delta_obj, "%D days %h:%m:%s")
    1 days 02:08:02
    >>> strfdelta(delta_obj, "%H hours and %M to go")
    20 hours and 18 to go
    """
    d = {"D": tdelta.days}
    d["H"], rem = divmod(tdelta.seconds, 3600)
    d["M"], d["S"] = divmod(rem, 60)
    d['h'], d['m'], d['s'] = (str(d[s]).zfill(2) for s in ('H', 'M', 'S'))
    t = DeltaTemplate(fmt)
    return t.substitute(**d)

def emitQueuePositions(inquiry):
    """Emit new queue positions"""
    from quupod.models import Inquiry
    unresolved = Inquiry.query.filter_by(
        queue_id=inquiry.queue_id,
        status='unresolved'
        ).order_by(asc(Inquiry.created_at)).all()
    indices = list(enumerate([i.id for i in unresolved], start=1))
    emit('update position',
        {'positions': json.dumps(indices)},
        broadcast=True,
        namespace='/q%d' % inquiry.queue_id)

def emitQueueInfo(queue):
    """
    Emit information about queue:
      (1) time to resolution
      (2) number of requests
    """
    from quupod.models import Inquiry
    emit('update student page',
        {
            'ttr': queue.ttr(),
            'nor': Inquiry.query.filter_by(queue_id=queue.id, status='unresolved').count()
        },
        broadcast=True,
        namespace='/q%d' % queue.id)
