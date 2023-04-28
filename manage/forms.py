from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SelectField, DateField, FloatField, DecimalField, EmailField, \
    BooleanField, PasswordField, RadioField
from models import Task
from wtforms import validators as v


class TaskFormEdit(FlaskForm):
    title = StringField(validators=[v.DataRequired()])
    description = TextAreaField(validators=[v.Optional()])
    user_id = SelectField(coerce=int, validators=[v.Optional()])
    board = SelectField(choices=('',) + Task.BOARDS)
    deadline = DateField(validators=[v.Optional()])
    estimate = DecimalField(validators=[v.Optional()])
    tags = StringField(validators=[v.Optional()])
    stage = StringField(validators=[v.Optional()])


class LoginForm(FlaskForm):
    name = StringField(validators=[v.DataRequired()])
    password = PasswordField(validators=[v.DataRequired()])
    remember_my = BooleanField()


class TaskCommentForm(FlaskForm):
    title = StringField(validators=[v.Optional()])
    description = TextAreaField(validators=[v.Optional()])

