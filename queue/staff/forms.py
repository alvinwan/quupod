from wtforms_alchemy import ModelForm, ModelFieldList
from wtforms.fields import FormField
from .models import Assignment, Problem


class AssignmentForm(ModelForm):
    """form for assignments"""
    class Meta:
        model = Assignment
        only = ('name', 'is_active')


class ProblemForm(ModelForm):
    """form for problems"""
    class Meta:
        model = Problem
        only = ('tag', 'description')
