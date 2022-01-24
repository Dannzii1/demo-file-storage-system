from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField, SubmitField, DecimalField
from wtforms.validators import InputRequired, Email, Regexp, NumberRange, ValidationError, EqualTo, DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import MultipleFileField
from flask_login import current_user

from app import allowed_uploads, app
from app.custom_form_validators import MaxContentLength
from app.models import Users


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired(message="Your First Name is Required")])
    last_name = StringField('Last Name', validators=[InputRequired(message="Your Last Name is Required")])
    username = StringField('Username', validators=[InputRequired(message="Username is Required")])
    email = StringField('Email Address', validators=[InputRequired(message="Email is Required"),
                                                     Email(message="Your Email is not a valid Email address")])
    password = PasswordField('Password', validators=[InputRequired(message="You must have a Password")])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[InputRequired(message="Please Retype your Password"),
                                                 EqualTo('password',
                                                       message='Passwords must'
                                                                 ' match')])


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(message="Username is Required")])
    password = PasswordField('Password', validators=[InputRequired(message="Password is Required")])


class UploadForm(FlaskForm):
    document = FileField('Document', validators=[
        FileRequired(message='You cannot submit an empty form'),
        FileAllowed(allowed_uploads, 'No Image Files'),
        MaxContentLength(content_length=app.config['MAX_CONTENT_LENGTH_PER_UPLOAD'])
    ], render_kw={'multiple': True})
    content_size = DecimalField(validators=[InputRequired(),
                                            NumberRange(min=app.config['MAX_CONTENT_LENGTH_PER_UPLOAD'],
                                                        max=app.config['MAX_CONTENT_LENGTH_PER_UPLOAD'])])

    def __init__(self):
        super(UploadForm, self).__init__()
        self.content_size.data = app.config['MAX_CONTENT_LENGTH_PER_UPLOAD']


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired(message="You must have a Password")])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[InputRequired(message="Please Retype your Password"),
                                                 EqualTo('password', message='Passwords must match')])


class RequestResetForm(FlaskForm):
    email = StringField('Email Address',
                        validators=[InputRequired(message="Your Email is Required"),
                                    Email(message="Your Email is not a valid Email address")])