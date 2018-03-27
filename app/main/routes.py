from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from datetime import datetime, timedelta, date, time
from app.main.forms import EditProfileForm, ClockForm
from app.models import Employee, TimeRecord
from app.main import bp
from app.main.functions import calculate_time_worked

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = ClockForm()
    if form.validate_on_submit():
        # Begin with an empty time_record
        time_record = TimeRecord(employee_id='', date='', start_time ='00:00:00', break_time ='00:00:00',
            end_time ='00:00:00')
        # Declare time format
        time_fmt = '%H:%M:%S'
        # Decalre date format
        date_fmt = '%Y-%m-%d'
        # Save today's datetime for checking for an existing time_record
        #today = datetime.strptime(str(form.date.data), "%Y-%m-%d %H:%M:%S.%f")
        # Retrieve employee from db
        user = Employee.query.filter_by(username=current_user.username).first()
        # Retrieve a list of all time_records for an employee
        tr = TimeRecord.query.filter_by(employee_id=user.employee_id).all()
        # If an employee has already clocked a time for today, update the existing time record
        for row in tr:
            if datetime.strptime(str(row.date), date_fmt) == datetime.strptime(
            datetime.strftime(form.date.data, date_fmt), date_fmt):
                time_record = row
        # Create variables to hold clock entries, set to 00:00:00 if no entry so far
        start = time_record.start_time
        break_total = time_record.break_time
        end = time_record.end_time
        # If there is a current time_record open for this employee,
        # confirm which clocking type the user has entered, and update the relevant time entry
        if time_record.employee_id != '':
            if form.clock_type.data == 'Clock-in':
                time_record.start_time = form.time.data
                start = form.time.data
            elif form.clock_type.data == 'Break':
                time_record.break_time = form.time.data
                break_total = form.time.data
            elif form.clock_type.data == 'Clock-out':
                time_record.end_time = form.time.data
                end = form.time.data
            # Calculate worked time
            worked = calculate_time_worked(end, break_total, start, time_fmt)
            # Set time_worked column in db object
            time_record.time_worked = worked
            # Commit changes to db
            db.session.commit()
            flash('Clock time recorded')
        else:
            # If there is no open time_record for today, we need to create one,
            # firstly, update the relevant time entry
            if form.clock_type.data == 'Clock-in':
                start = form.time.data
            elif form.clock_type.data == 'Break':
                break_total = form.time.data
            elif form.clock_type.data == 'Clock-out':
                end = form.time.data
            # Calculate worked time
            worked = calculate_time_worked(end, break_total, start, time_fmt)
            # Create new time_record and insert values
            time = TimeRecord(employee_id=user.employee_id, date=form.date.data, start_time=start,
                break_time=break_total, end_time=end, time_worked=worked)
            # Add the new time record to the db session
            db.session.add(time)
            # Commit changes to the db
            db.session.commit()
            flash('Clock time recorded')

        return redirect(url_for('main.index'))
    return render_template("index.html", title='Home Page', form=form)

@bp.route('/user/<username>')
@login_required
def user(username):
    user = Employee.query.filter_by(username=username).first_or_404()
# Do not allow employee's to access each others accounts, restrict this activity to admin accounts.
    if user.username != current_user.username:
        if current_user.is_admin == 'y':
            return render_template('profile.html', user=user)
        else:
            return redirect(url_for('main.index'))
    else:
        return render_template('profile.html', user=user)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    # If form is submitted, update DB columns using form data
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.address1 = form.address1.data
        current_user.address2 = form.address2.data
        current_user.address3 = form.address3.data
        current_user.postcode = form.postcode.data
        current_user.phone_number = form.phone_number.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    # If GET request, pre-populate form data with DB entries
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.address1.data = current_user.address1
        form.address2.data = current_user.address2
        form.address3.data = current_user.address3
        form.postcode.data = current_user.postcode
        form.phone_number.data = current_user.phone_number
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
