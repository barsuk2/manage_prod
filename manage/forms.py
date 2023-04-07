from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SelectField


class TaskFormEdit(FlaskForm):
    title = StringField()
    description = StringField()
    user = SelectField(coerce=int)

