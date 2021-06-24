"""Form object declaration."""

from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField, IntegerField, FieldList, FormField
from wtforms.validators import DataRequired, Optional



class Title(FlaskForm):
    """Search by Title"""
    title = StringField('Title',[DataRequired()])
    submit = SubmitField('Submit')


class TitleYear(FlaskForm):
    """Search by Title and Range of Years"""
    title = StringField(
        'Title',
        [DataRequired()]
    )
    min_year = IntegerField(
        'Release Year >=',
        [Optional()]
    )
    max_year = IntegerField(
        'Release Year <=',
        [Optional()]
    )
    submit = SubmitField('Submit')


class Omnibus(FlaskForm):
    """Search by Many Parameters"""
    #TODO
    submit = SubmitField('Submit')