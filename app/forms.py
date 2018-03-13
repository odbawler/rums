from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from wtforms_components import TimeField
from app.models import Employee

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterEmployeeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        # Method to ensure username is unique
        employee = Employee.query.filter_by(username=username.data).first()
        if employee is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        # Method to ensure email is unique
        employee = Employee.query.filter_by(email=email.data).first()
        if employee is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address1 = StringField('Address 1', validators=[DataRequired()])
    address2 = StringField('Address 2')
    address3 = StringField('Address 3')
    postcode = StringField('Postcode', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = Employee.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Username is taken. Please choose a different username.')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Email Me ')

class PasswordResetForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    conf_password = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset your password')

class ClockForm(FlaskForm):
    start_time = TimeField('Start')
    break_time = TimeField('Break')
    end_time = TimeField('Finish')
    submit = SubmitField('Submit')
