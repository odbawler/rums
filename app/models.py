from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
from sqlalchemy import DateTime
from flask import current_app
import jwt

class Employee(UserMixin, db.Model):
    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True)
    username = db.Column(db.String, index=True, unique=True)
    email = db.Column(db.String, index=True, unique=True)
    password = db.Column(db.String)
    address1 = db.Column(db.String)
    address2 = db.Column(db.String)
    address3 = db.Column(db.String)
    postcode = db.Column(db.String)
    phone_number = db.Column(db.String)
    date_of_birth = db.Column(db.Date)
    line_manager_id = db.Column(db.Integer)
    leave_allowance = db.Column(db.Numeric)
    is_admin = db.Column(db.String)

    employeestime = db.relationship("EmployeeTime", cascade="all,delete", backref="Employee")
    timerecords = db.relationship("TimeRecord", cascade="all,delete", backref="Employee")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return self.employee_id

    def check_admin(self):
        return self.is_admin

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.employee_id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return Employee.query.get(id)

    def __repr__(self):
        return " name: %s, id: %s" % (self.name, self.employee_id)

@login.user_loader
def load_employee(id):
    return Employee.query.get(int(id))

class EmployeeTime(db.Model):
    employee_time_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'))
    hours_a_week = db.Column(db.Numeric)
    hours_a_day = db.Column(db.Time)
    flexi = db.Column(db.String)
    last_updated = db.Column(DateTime)
    created = db.Column(db.Date)
    employee = db.relationship(Employee, backref='time')

    def __repr__(self):
        return '<employee_time {}>'.format(self.flexi)

    def get_flexi(self):
        hours, minutes = current.split(':')
        return hours + 'hours ' + minutes + 'minutes'

class TimeRecord(db.Model):
    time_record_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'))
    date = db.Column(db.Date)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    start_break = db.Column(db.Time, nullable=True)
    end_break = db.Column(db.Time, nullable=True)
    total_break = db.Column(db.Time, nullable=True)
    time_worked = db.Column(db.Time, nullable=True)
    sufficient = db.Column(db.String, nullable=True)
    absent = db.Column(db.String, nullable=True)
    employee = db.relationship(Employee, backref='time records')

    def __repr__(self):
        return '<time_record {}>'.format(self.date)

    def get_date(self):
        return self.date

    def get_clock_in(self):
        return self.start_time

    def get_clock_out(self):
        return self.end_time

    def get_start_break(self):
        return self.start_break

    def get_end_break(self):
        return self.end_break

    def get_time_worked(self):
        return self.time_worked

class LineManager (db.Model):
    line_manager_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'))

    def __repr__(self):
        return '<line_manager {}>'.format(self.line_manager_id)

class LeaveRequest (db.Model):
    leave_request_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'))
    request_type = db.Column(db.String)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String)

    def __repr__(self):
        return '<leave_request {}>'.format(self.status)
