from wtforms_alchemy import ModelForm, ModelFieldList
from wtforms.fields import FormField
from .models import Assignment, Problem


class AssignmentForm(ModelForm):
    """form for assignments"""
    class Meta:
        model = Assignment


class ProblemForm(ModelForm):
    """form for problems"""
    class Meta:
        model = Problem

    assignment_id = ModelFieldList(FormField(AssignmentForm))
