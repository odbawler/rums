from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from datetime import datetime
from wtforms.validators import ValidationError, DataRequired, Email
from wtforms_components import TimeField, SelectField, DateField
from app.models import Employee

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

class ClockForm(FlaskForm):
    clock_type = SelectField(choices=[('Clock-in', 'Clock-in'), ('Start-Break', 'Start-Break')
    , ('End-Break', 'End-Break'), ('Clock-out', 'Clock-out'), ('Absent', 'Absent')
    , ('Remove Absence', 'Remove Absence'), ('Clear Day', 'Clear Day')], validators=[DataRequired()])
    time = TimeField('Time', default=datetime(1900,1,1,0,0,0))
    date = DateField('Date', default=datetime.now())
    submit = SubmitField('Submit')

    def validate_date(self, date):
        if date.data > datetime.now().date():
            raise ValidationError('Cannot record time in the future.')
