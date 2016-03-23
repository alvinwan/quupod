from string import Template

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
