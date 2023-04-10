from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SelectField, DateField, FloatField, DecimalField
from models import Task
from wtforms import validators as v


class TaskFormEdit(FlaskForm):
    title = StringField(validators=[v.Optional()])
    description = TextAreaField()
    user_id = SelectField(coerce=int)
    board = SelectField(choices=('',) + Task.BOARDS)
    deadline = DateField()
    estimate = DecimalField()
    tags = StringField()

