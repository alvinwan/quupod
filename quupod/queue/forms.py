from wtforms_alchemy import ModelForm, ModelFieldList
import wtforms as wtf
from quupod.models import Queue
from quupod.defaults import default_queue_roles
from wtforms.validators import InputRequired, DataRequired, Optional
from quupod.forms import choicify
from flask import g


class QueueForm(ModelForm):
    """form for queues"""

    class Meta:
        model = Queue
        only = ('name', 'description', 'url')

    category = wtf.SelectField(
        'Category',
        choices=choicify(default_queue_roles.keys()),
        coerce=str)

assignment_description = '<b>Use the following abbreviations</b>: <code>hw</code> for "homework", <code>proj</code> for "project", and <code>dis</code> for "discussion".'


class InquiryForm(ModelForm):
    """form for placing inquiries"""

    name = wtf.StringField('Name',
        description='Your full name', validators=[DataRequired()])
    category = wtf.SelectField('Category',
        description='What type of inquiry are you submitting?', coerce=str, validators=[Optional()])
    location = wtf.SelectField('Location',
        description='Help us find you!', coerce=str, validators=[Optional()])
    assignment = wtf.StringField('Assignment',
        description=assignment_description, validators=[InputRequired()])
    problem = wtf.StringField('Problem',
        description='Be specific about which part, and do not include spaces or punctuation. For example, to specify problem 1 part a, only use <code>1a</code>.', validators=[Optional()])

    def __iter__(self):
        fields = []
        for k, v in self._fields.items():
            if (k == 'location' and not g.queue.setting('locations').enabled)\
                or (k == 'category' and not g.queue.setting(
                    name='inquiry_types').enabled):
                continue
            else:
                fields.append(v)
        return iter(fields)
