from flask import render_template, flash, redirect, url_for, request, make_response
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from datetime import *
from app.main.forms import EditProfileForm, ClockForm
from app.models import Employee, TimeRecord, EmployeeTime
from app.main import bp
from app.main.functions import calculate_time_worked, calculate_break_time, format_timedelta, subtract_daily_hrs, add_worked_hrs

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = ClockForm()
    # Declare time format
    time_fmt = '%H:%M:%S'
    # Decalre date format
    date_fmt = '%Y-%m-%d'
    dt = datetime.strptime('00:00:00', time_fmt).time()
    delta = timedelta(hours=0,minutes=0,seconds=0)
    print('delta')
    print(delta)
    et = EmployeeTime.query.filter_by(employee_id=current_user.employee_id).first()
    if form.validate_on_submit():
        # Prevent recording time in the future (for the same day)
        if form.date.data == datetime.now().date() and str(form.time.data) > str(datetime.now().time()):
            return redirect(url_for('main.index')), flash("Cannot record time in the future!", 'danger')
        else:
            # Begin with an empty time_record
            time_record = TimeRecord(employee_id='', date='', start_time=dt, end_time=dt, start_break=dt,
            end_break=dt, total_break = dt)

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
            break_start = time_record.start_break
            break_end = time_record.end_break
            end = time_record.end_time

            # If the user wants to record a the current time, we use this formatted datetime.now().time() (no ms)
            format_now = str(datetime.now().time())
            time_to_rec = datetime.strptime(format_now.split(".")[0], time_fmt).time()

            # If the user wants the current time, the time data will be left at midnight.
            # Use this check to determine whether to use the timefield data or the datetime.now().time()
            if str(form.time.data) != '00:00:00':
                time_to_rec = form.time.data

            # If there is a current time_record open for this employee,
            # confirm which clocking type the user has entered, and update the relevant time entry
            if time_record.employee_id != '':
                if form.clock_type.data == 'Clock-in':
                    # (clocking corrections) - Cannot record clock-in time after clock-out time
                    if time_record.end_time != dt:
                        if time_to_rec > time_record.end_time:
                            return redirect(url_for('main.index')), flash("Cannot clock in after clock out time!", 'danger')
                    time_record.start_time = time_to_rec
                    start = time_to_rec
                elif form.clock_type.data == 'Start-Break':
                    # Must clock-in before starting break
                    if time_record.start_time != dt:
                        if time_to_rec < time_record.start_time:
                            return redirect(url_for('main.index')), flash("Cannot start break before clocking in!", 'danger')
                    time_record.start_break = time_to_rec
                    break_start = time_to_rec
                elif form.clock_type.data == 'End-Break':
                    # Must clock in before taking a break
                    if time_record.start_time != dt:
                        if time_to_rec < time_record.start_time:
                            return redirect(url_for('main.index')), flash("Cannot end break before clocking in!", 'danger')
                    # Cannot end break before starting break
                    if time_record.start_break == dt:
                        response = make_response()
                        return redirect(url_for('main.index')), flash("Must start break before ending break!", 'danger')
                    # End break time cannot be before start break time
                    if time_to_rec < time_record.start_break:
                        return redirect(url_for('main.index')), flash("Cannot end break before start of break!", 'danger')
                    time_record.end_break = time_to_rec
                    break_end = time_to_rec
                elif form.clock_type.data == 'Clock-out':
                    # Must clock-in before clocking out
                    if time_record.start_time == dt:
                        return redirect(url_for('main.index')), flash("Must clock in before clocking out!", 'danger')
                    # Cannot record clock-out time before clock-in time
                    if time_record.start_time != dt:
                        if time_to_rec < time_record.start_time:
                            return redirect(url_for('main.index')), flash("Cannot clock out before clocking in!", 'danger')
                    time_record.end_time = time_to_rec
                    end = time_to_rec

                # Calculate break total if both break times are recorded
                break_total = delta
                if(time_record.start_break != dt and
                  time_record.end_break != dt):
                  break_total = calculate_break_time(break_start, break_end, time_fmt)
                # this shoule be str()? test after end problem
                if(time_record.start_time != dt and
                  time_record.end_time != dt):
                    print("calcualting time worked")
                    # We can send the start time as datetime or datetime.time due to the auto/manual time entering routes.
                    # To deal with this -- if we have a datetime, we send only the .time() element
                    if isinstance(start, datetime):
                        worked = calculate_time_worked(end, break_total, start.time(), time_fmt)
                    else:
                        # Calculate worked time
                        worked = calculate_time_worked(end, break_total, start, time_fmt)
                else:
                    worked = dt

                # Set time_worked column in db object
                time_record.time_worked = worked

                # Set total_break in db
                time_record.total_break = break_total

                # Commit changes to db
                db.session.commit()

                if str(form.time.data) != '00:00:00':
                    flash('Recorded: ' +  form.clock_type.data + ' ' + str(form.date.data) + ' ' + str(form.time.data))
                else:
                    flash('Recorded: ' +  form.clock_type.data + ' ' + str(form.date.data) + ' ' + str(datetime.now().time()).split(".")[0])
            else:
                # If there is no open time_record for today, we need to create one.
                # Firstly, update the relevant time entry
                if form.clock_type.data == 'Clock-in':
                    # (clocking corrections) - Cannot record clock-in time after clock-out time
                    if time_record.end_time != dt:
                        if time_to_rec > time_record.end_time:
                            return redirect(url_for('main.index')), flash("Cannot clock in after clock out time!", 'danger')
                    start = time_to_rec
                elif form.clock_type.data == 'Start-Break':
                    # Must clock-in before starting break
                    if time_record.start_time != dt:
                        if time_to_rec < time_record.start_time:
                            return redirect(url_for('main.index')), flash("Cannot start break before clocking in!", 'danger')
                    break_start = time_to_rec
                elif form.clock_type.data == 'End-Break':
                    # Must clock in before taking a break
                    if time_record.start_time != dt:
                        if time_to_rec < time_record.start_time:
                            return redirect(url_for('main.index')), flash("Cannot end break before clocking in!", 'danger')
                    # Cannot end break before starting break
                    if time_record.start_break == dt
                        return redirect(url_for('main.index')), flash("Must start break before ending break!", 'danger')
                    # End break time cannot be before start break time
                    if time_to_rec < time_record.start_break:
                        return redirect(url_for('main.index')), flash("Cannot end break before start of break!", 'danger')
                    break_end = time_to_rec
                elif form.clock_type.data == 'Clock-out':
                    # Must clock-in before clocking out
                    if time_record.start_time == dt:
                        return redirect(url_for('main.index')), flash("Must clock in before clocking out!", 'danger')
                    # Cannot record clock-out time before clock-in time
                    if time_record.start_time != dt:
                        if time_to_rec < time_record.start_time:
                            return redirect(url_for('main.index')), flash("Cannot clock out before clocking in!", 'danger')
                    end = time_to_rec

                # Calculate break total if both break times are recorded
                break_total = delta
                if(time_record.start_break != dt and
                  time_record.end_break != dt):
                  break_total = calculate_break_time(break_start, break_end, time_fmt)

                time = TimeRecord(employee_id=user.employee_id, date=form.date.data, start_time=start,
                 end_time=end, start_break=break_start, end_break=break_end, total_break=break_total, time_worked=dt)

                # Add the new time record to the db session
                db.session.add(time)

                # Commit changes to the db
                db.session.commit()

                if str(form.time.data) != '00:00:00':
                    flash('Recorded: ' +  form.clock_type.data + ' ' + str(form.date.data) + ' ' + str(form.time.data))
                else:
                    flash('Recorded: ' +  form.clock_type.data + ' ' + str(form.date.data) + ' ' + str(datetime.now().time()).split(".")[0])

            return redirect(url_for('main.index'))
    return render_template("index.html", title='Home Page', form=form, flexi=et.flexi)

# This route appends the users employee id value to the url in order to prevent users from hitting the URL directly,
# This ofcourse can still happen, so to prevent a user updating flexi for another user, I catch the
# type error to redirect to a 404 page, as the username and employee ID will not match. In the case a user tries to
# hit the url appending an employee_id that does no exist, the atrribute error is caught to display the 404.
@bp.route('/update_flexi/<variable>')
@login_required
def update_flexi(variable):
    try:
        user = Employee.query.filter_by(username=current_user.username).first()
        et = EmployeeTime.query.filter_by(employee_id=variable).first()
        trs = TimeRecord.query.filter_by(employee_id=variable).all()
        print('trs')
        print(trs)
        now = datetime.today()
        delay = timedelta(minutes=5)
        base_time = datetime.strptime('00:00:00', '%H:%M:%S').time()
        worked_hrs_delta = datetime.combine(date.min, base_time) - datetime.min
        daily_hrs_delta = datetime.combine(date.min, base_time) - datetime.min
        # hrs to add per working day
        daily_hrs_time = datetime.combine(date.min, et.hours_a_day) - datetime.min
        for row in trs:
            if row.date >= et.last_updated.date():
                # total expected hours since last update
                daily_hrs_delta += daily_hrs_time
                # total worked hours since last update
                time_worked_delta = datetime.combine(date.min, row.time_worked) - datetime.min
                worked_hrs_delta += time_worked_delta

        # Implement 5 minute cooldown period for refreshing flexi
        if now - et.last_updated > delay:
            # If daily hrs have already been applied today, do not add them again
            if et.last_updated.date() != datetime.today().date():
                # Print out values as they are manipulated in case of investigation
                print("expected hours")
                print(daily_hrs_delta)
                print("worked hours")
                print(worked_hrs_delta)

                # Retrieve current flexi value
                current_flexi = et.flexi
                print("current flexi")
                print(current_flexi)

                # Subtract accumulated daily working hours since last update
                subtracted_flexi = subtract_daily_hrs(current_flexi, format_timedelta(daily_hrs_delta))
                print("flexi - expected hours")
                print(subtracted_flexi)

                # Add total worked hours since last update
                calculated_flexi = add_worked_hrs(subtracted_flexi, format_timedelta(worked_hrs_delta))
                print("flexi + worked hours")
                print(calculated_flexi)

                # Set new updated flexi value and update last_updated column
                et.flexi = calculated_flexi
                et.last_updated = datetime.now()

                print('updating flexi time for')
                print(current_user)
                db.session.commit()
                response = make_response(str(et.flexi))
                response.headers['Content-Type'] = 'text/xml; charset=utf-8'
                return response
            else:
                # for clocking corrections calculate from beginning of time_records
                et.last_updated = datetime(2018, 1, 1, 0, 0, 0, 0)
                et.flexi = '00:00'
                worked_delta = datetime.combine(date.min, base_time) - datetime.min
                daily_delta = datetime.combine(date.min, base_time) - datetime.min
                for row in trs:
                    if row.date >= et.last_updated.date():
                        # total expected hours since last update
                        daily_delta += daily_hrs_time

                        # total worked hours since last update
                        time_worked_delta = datetime.combine(date.min, row.time_worked) - datetime.min
                        worked_delta += time_worked_delta

                print("expected hours")
                print(daily_delta)
                print("worked hhours")
                print(worked_delta)

                # Retrieve current flexi value
                current_flexi = et.flexi
                print("current flexi")
                print(current_flexi)

                # Subtract accumulated daily working hours
                subtracted_flexi = subtract_daily_hrs(current_flexi, format_timedelta(daily_delta))
                print("flexi - expected hours")
                print(subtracted_flexi)

                # Add total worked hours
                calculated_flexi = add_worked_hrs(subtracted_flexi, format_timedelta(worked_delta))
                print("flexi + worked hours")
                print(calculated_flexi)

                # Set new updated flexi value and update last_updated column
                et.flexi = calculated_flexi

                et.last_updated = datetime.now()
                db.session.commit()
                response = make_response(str(et.flexi))
                return response, flash("Expected hours already added, adjusted for working hours recorded.")
        else:
            response = make_response()
            return response, flash("Must wait 5 minutes before refreshing flexi!", 'danger')
    except TypeError:
        return render_template('errors/404.html', title='Page Not Found')
    except AttributeError:
        return render_template('errors/404.html', title='Page Not Found')

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
        # Validate post code is no longer than 7 chars (allow for space eg . PL4 888 - PL4888)
        if len(form.postcode.data) != 7:
            return redirect(url_for('main.edit_profile')), flash("Postcode is wrong length.", 'danger')
        current_user.postcode = form.postcode.data
        # Validate UK phone number is 11 charcters long and begins with '07'
        if len(form.phone_number.data) != 11:
            return redirect(url_for('main.edit_profile')), flash("Phone number is wrong length.", 'danger')
        if form.phone_number.data[0] != '0' or form.phone_number.data[1] != '7':
            return redirect(url_for('main.edit_profile')), flash("Phone number is invalid.", 'danger')
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
