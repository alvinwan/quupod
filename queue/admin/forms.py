from wtforms_alchemy import ModelForm, ModelFieldList
from wtforms.fields import FormField
import wtforms as wtf
from .models import Assignment, Event


class AssignmentForm(ModelForm):
    """form for assignments"""
    class Meta:
        model = Assignment
        only = ('name', 'problems', 'is_active')


class EventForm(ModelForm):
    """form for events"""
    class Meta:
        model = Event
        only = ('name', 'description', 'location')

    start = wtf.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    end = wtf.DateTimeField(format='%Y-%m-%d %H:%M:%S')
