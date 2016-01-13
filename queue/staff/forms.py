from wtforms_alchemy import ModelForm, ModelFieldList
from wtforms.fields import FormField
from .models import Assignment


class AssignmentForm(ModelForm):
    """form for assignments"""
    class Meta:
        model = Assignment
        only = ('name', 'problems', 'is_active')
