from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import (DataRequired, Regexp, ValidationError,
                               Length, EqualTo)
from email_validator import validate_email, EmailNotValidError
from models import User

def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')


class NewEntryForm(Form):
    title = StringField(
        'Title',
        validators=[
            DataRequired(),
        ])
    date = StringField(
        'Date',
        validators=[
            DataRequired(),
            Regexp(
                r'(([1-2][0-9])|(0[1-9])|([1-9])|(3[0-1]))/((1[0-2])|(0[1-9])|([1-9]))/[0-9]{4}',
                message=("Please format your date dd/mm/yyyy.")
            ),
        ]
    )
    time_spent = StringField(
        'Time Spent (hours)',
        validators=[
            DataRequired(),
        ])
    learnt = TextAreaField(
        'What I Learned',
        validators=[
            DataRequired(),
        ])
    resources = TextAreaField(
        'Recources to Remember',
        validators=[
            DataRequired(),
        ])
    tags = StringField(
        'Tags'
    )


class RegisterForm(Form):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters, "
                         "numbers, and underscores only.")
            ),
            name_exists
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=2),
            EqualTo('password2', message='Passwords must match')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
    )

class LoginForm(Form):
    username = StringField(
        'Username', 
        validators=[
            DataRequired(),
            ])
    password = PasswordField('Password', validators=[DataRequired()])