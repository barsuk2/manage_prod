import datetime

from flask_wtf import FlaskForm
from sqlalchemy import extract
from wtforms import TextAreaField, StringField, SelectField, DateField, FloatField, DecimalField, EmailField, \
    BooleanField, PasswordField, RadioField, SelectMultipleField

from flask import current_app
from core import db
from models import Task
from wtforms import validators as v


class TaskFormEdit(FlaskForm):
    title = StringField(validators=[v.DataRequired()])
    description = TextAreaField(validators=[v.Optional()])
    user_id = SelectField(coerce=int, validators=[v.Optional()])
    board = SelectField(choices=[('', '')] + [(x, y) for x, y in Task.BOARDS.items()])
    deadline = DateField(validators=[v.Optional()])
    estimate = DecimalField(validators=[v.Optional()])
    tags = StringField(validators=[v.Optional()])
    stage = StringField(validators=[v.Optional()])
    importance = SelectField(choices=[('', 'Нет')] + [(x, y) for x, y in Task.IMPORTANCE.items()],
                             validators=[v.Optional()])
    # comments = TextAreaField(validators=[v.Optional()])


class LoginForm(FlaskForm):
    name = StringField(validators=[v.DataRequired()])
    password = PasswordField(validators=[v.DataRequired()])
    remember_my = BooleanField()


class TaskCommentForm(FlaskForm):
    title = StringField(validators=[v.Optional()])
    description = TextAreaField(validators=[v.Optional()])


class UserForm(FlaskForm):
    name = StringField('Имя', validators=[v.DataRequired()])
    email = EmailField('Email', validators=[v.DataRequired()])
    banned = BooleanField(default=None)
    password = StringField()
    mobile = StringField()
    telegram = StringField()


class StatisticFilter(FlaskForm):
    user = SelectField(validators=[v.Optional()])
    period = SelectField(validators=[v.Optional()])


class TaskFilter(FlaskForm):
    search_word = StringField(validators=[v.Optional()])


class CardForm(FlaskForm):
    category = StringField(validators=[v.Optional()])
    subcategory = StringField(validators=[v.Optional()])
    questions = StringField(validators=[v.Optional()])
    response = TextAreaField(validators=[v.Optional()])


class ViewCardForm(FlaskForm):
    category = SelectMultipleField(validators=[v.Optional()])
