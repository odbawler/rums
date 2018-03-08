from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Employee(UserMixin, db.Model):
    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True)
    username = db.Column(db.String, index=True, unique=True)
    email = db.Column(db.String, index=True, unique=True)
    password = db.Column(db.String)
    address1 = db.Column(db.String)
    address2 = db.Column(db.String)
    address3 = db.Column(db.String)
    postcode = db.Column(db.String(7))
    phone_number = db.Column(db.String(11))
    date_of_birth = db.Column(db.Date)
    line_manager_id = db.Column(db.Integer)
    leave_allowance = db.Column(db.Numeric)
    is_admin = db.Column(db.String)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return self.employee_id

    def check_admin(self):
        return self.is_admin

    def __repr__(self):
        return '<employee {}>'.format(self.username)

@login.user_loader
def load_employee(id):
    return Employee.query.get(int(id))

class employee_time(db.Model):
    employee_time_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'))
    weekly_hours = db.Column(db.Numeric)
    flexi_total = db.Column(db.Numeric)

    def __repr__(self):
        return '<employee_time {}>'.format(self.body)

class time_record(db.Model):
    time_record_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'))
    date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    break_time = db.Column(db.Time)
    time_worked = db.Column(db.Time)

    def __repr__(self):
        return '<time_record {}>'.format(self.body)

class line_manager (db.Model):
    line_manager_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'))

    def __repr__(self):
        return '<line_manager {}>'.format(self.body)

class leave_request (db.Model):
    leave_request_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'))
    request_type = db.Column(db.String)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String)

    def __repr__(self):
        return '<leave_request {}>'.format(self.body)
