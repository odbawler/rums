from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
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
    hours = StringField('Hours', validators=[DataRequired()])
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

    def validate_password(self, password):
        # Ensure password is 8 or more chars
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters.')
        # Check for uppercase chars
        lower = passsword.lower()
        if lower  == password:
            raise ValidationError('Password must contain atleast 1 uppercase character.')
        # Check for lowercase chars
        upper = passsword.upper()
        if upper  == password:
            raise ValidationError('Password must contain atleast 1 lowercase character.')
        # Check for number
        if not password.isalnum():
            raise ValidationError('Password must contain atleast 1 number.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Email Me ')

class PasswordResetForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    conf_password = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset your password')

    def validate_password(self, password):
        # Ensure password is 8 or more chars
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters.')
        # Check for uppercase chars
        lower = passsword.lower()
        if lower  == password:
            raise ValidationError('Password must contain atleast 1 uppercase character.')
        # Check for lowercase chars
        upper = passsword.upper()
        if upper  == password:
            raise ValidationError('Password must contain atleast 1 lowercase character.')
        # Check for number
        if not password.isalnum():
            raise ValidationError('Password must contain atleast 1 number.')
