from app.models import Employee, TimeRecord, EmployeeTime
from app import db
from app import create_app
from flask import current_app


def update_flexi():
    employees = Employee.query.all()
    for e in employees:
        et = EmployeeTime.query.filter_by(employee_id=e.get_id()).first()
        daily_hrs = et.weekly_hours/5
        et.flexi += daily_hrs
        print('updating flexi time')
        db.session.commit()
