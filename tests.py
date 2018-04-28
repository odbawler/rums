from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.models import Employee, EmployeeTime, TimeRecord
from app.main.functions import calculate_time_worked, calculate_break_time, format_timedelta, subtract_daily_hrs, add_worked_hrs

from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgres://localhost/'

class EmployeeCreation(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        e = Employee(username='Joseph')
        e.set_password('joey123')
        self.assertFalse(e.check_password('joeswrongpassword'))
        self.assertFalse(e.check_password('joeey123'))
        self.assertFalse(e.check_password('joey124'))
        self.assertTrue(e.check_password('joey123'))

class TimeCalculations(unittest.TestCase):
        def setUp(self):
            self.app = create_app(TestConfig)
            self.app_context = self.app.app_context()
            self.app_context.push()
            db.create_all()
            newemployee = Employee(name='Joseph Bloggs', username='joe_bloggs', email='jblgs@email.email', is_admin='n')
            db.session.add(newemployee)
            db.session.commit()
            employeetime = EmployeeTime(employee_id = newemployee.get_id(), hours_a_week = 37,
             hours_a_day = '07:24', flexi = '00:00', last_updated = datetime.now())
            db.session.add(employeetime)
            db.session.commit()

        def tearDown(self):
            db.session.remove()
            db.drop_all()
            self.app_context.pop()

        def test_subtracting_daily_hours(self):
            # Testing the subtract daily hours method where the daily working hours are deducted from
            # the current total flexi value. Test covers deducting the daily hours from a blank flexi
            # value, deducting the daily hours from an already negative flexi value, and then deducting
            # the daily hours from a positive flexi to finish with a negative flexi value.
            user = Employee.query.filter_by(username='joe_bloggs').first()
            et = EmployeeTime.query.filter_by(employee_id=user.get_id()).first()
            flexi = et.flexi
            flexi = subtract_daily_hrs(flexi, '07:24')
            self.assertTrue(flexi == '-7:24')
            flexi = subtract_daily_hrs(flexi, '07:24')
            self.assertTrue(flexi == '-14:48')
            flexi = '2:0'
            flexi = subtract_daily_hrs(flexi, '07:24')
            self.assertTrue(flexi == '-5:24')


        def test_adding_worked_hours(self):
            # Testing the add worked hours method where the total worked hours are added to the current
            # flexi value. Test covers adding worked hours to blank flexi, adding worked hours to positive
            # flexi, adding worked hours to a negative flexi that is still negative and then adding worked
            # hours to a negative flexi that turns positive.
            user = Employee.query.filter_by(username='joe_bloggs').first()
            et = EmployeeTime.query.filter_by(employee_id=user.get_id()).first()
            flexi = et.flexi
            flexi = add_worked_hrs(flexi, '07:24')
            self.assertTrue(flexi == '7:24')
            flexi = add_worked_hrs(flexi, '07:24')
            self.assertTrue(flexi == '14:48')
            flexi = '-12:24'
            flexi = add_worked_hrs(flexi, '07:24')
            self.assertTrue(flexi == '-5:0')
            flexi = add_worked_hrs(flexi, '07:24')
            self.assertTrue(flexi == '2:24')

        def test_add_subtract_negative(self):
            # Tests adding worked hours and subtracting expected hours to change the flexi value in and out
            # of positive and negative values, ensuring the value is always accurate.
            user = Employee.query.filter_by(username='joe_bloggs').first()
            et = EmployeeTime.query.filter_by(employee_id=user.get_id()).first()
            flexi = et.flexi
            flexi = add_worked_hrs(flexi, '03:24')
            self.assertTrue(flexi == '3:24')
            flexi = subtract_daily_hrs(flexi, '07:24')
            self.assertTrue(flexi == '-4:0')
            flexi = add_worked_hrs(flexi, '03:24')
            self.assertTrue(flexi == '-0:36')
            flexi = add_worked_hrs(flexi, '0:40')
            self.assertTrue(flexi == '0:4')

        def test_calculating_break_time(self):
            # Tests the method to calculate the difference between the start break time and end break time.
            time_fmt = '%H:%M:%S'
            breaktime = calculate_break_time(datetime.strptime('12:00:00', time_fmt).time(), datetime.strptime('12:30:00', time_fmt).time(), time_fmt)
            self.assertTrue(str(breaktime) == '0:30:00')
            breaktime = calculate_break_time(datetime.strptime('12:00:00', time_fmt).time(), datetime.strptime('13:30:00', time_fmt).time(), time_fmt)
            self.assertTrue(str(breaktime) == '1:30:00')

        def test_calculating_time_worked(self):
            # Tests the method to calculate time worked. Tests calculating time worked with and without break time entries. 
            time_fmt = '%H:%M:%S'
            worktime = calculate_time_worked(datetime.strptime('17:00:00', time_fmt).time(), timedelta(minutes=30), datetime.strptime('09:00:00', time_fmt).time(), time_fmt)
            self.assertTrue(str(worktime.time()) == '07:30:00')
            worktime = calculate_time_worked(datetime.strptime('17:00:00', time_fmt).time(), timedelta(minutes=0), datetime.strptime('09:00:00', time_fmt).time(), time_fmt)
            self.assertTrue(str(worktime.time()) == '08:00:00')
            worktime = calculate_time_worked(datetime.strptime('13:00:00', time_fmt).time(), timedelta(minutes=60), datetime.strptime('07:00:00', time_fmt).time(), time_fmt)
            self.assertTrue(str(worktime.time()) == '05:00:00')
            worktime = calculate_time_worked(datetime.strptime('12:00:00', time_fmt).time(), timedelta(minutes=30), datetime.strptime('11:00:00', time_fmt).time(), time_fmt)
            self.assertTrue(str(worktime.time()) == '00:30:00')




if __name__ == '__main__':
    unittest.main(verbosity=2)
