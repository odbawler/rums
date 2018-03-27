from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.models import Employee

from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgres://localhost/'

class EmployeeModelCase(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main(verbosity=2)
