from app import create_app, db, admin
from app.models import Employee, EmployeeTime, TimeRecord
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView
from flask import render_template

app = create_app()


class EmployeeView(ModelView):

    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.is_admin == 'y':
                return True
        return False


    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    can_view_details = True
    column_exclude_list = ['password']
    column_searchable_list = ['name', 'username', 'email', 'postcode', 'phone_number']
    form_excluded_columns = ['time', 'time records', 'line_manager_id', 'password']
    edit_modal = True
    can_create = False


class EmployeeTimeView(ModelView):

    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.is_admin == 'y':
                return True
        return False


    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))
        
    can_view_details = True
    can_create = False

class TimeRecordView(ModelView):

    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.is_admin == 'y':
                return True
        return False


    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    can_view_details = True
    can_create = False

admin.add_view(EmployeeView(Employee, db.session))
admin.add_view(EmployeeTimeView(EmployeeTime, db.session))
admin.add_view(TimeRecordView(TimeRecord, db.session))

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'employee': employee}
