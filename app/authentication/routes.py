from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app.authentication.email import send_password_reset_email
from app.authentication import bp
from datetime import datetime, timedelta, date, time
from app import db
from app.authentication.forms import LoginForm, RegisterEmployeeForm, ResetPasswordRequestForm, PasswordResetForm
from app.models import Employee, TimeRecord, EmployeeTime

@bp.route('/login', methods=['GET', 'POST'])
def login():
    #if user is already logged in, redirect to index page
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    # Add admin account if it does not exist (first time startup)
    anyaccounts = Employee.query.first()
    if anyaccounts is None:
        admin = Employee(username='admin', is_admin='y')
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
        # Commit admin account to db so we can retrieve the employee_id to enter into employee_time.
        employeetime = EmployeeTime(employee_id = admin.get_id(), hours_a_week = 0,
            hours_a_day = '00:00' , flexi = '00:00:00')
        db.session.add(employeetime)
        db.session.commit()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(username=form.username.data).first()
        # Check employee is in the DB and password is correct
        if employee is None or not employee.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('authentication.login'))
        # Log the user in with flask_login, remember_me=True creates a cookie to keep the user logged in
        # if they close their browser without logging out
        login_user(employee, remember=form.remember_me.data)
        next_page = request.args.get('next')
        # Check netloc to ensure url is relative to prevent redirection to external site
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('authentication/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.is_admin == 'y':
        form = RegisterEmployeeForm()
        if form.validate_on_submit():
            # If this is the first registered user, give them admin priveldges
            is_first_user = len(Employee.query.all())
            admin = 'n'
            if is_first_user == 0:
                admin = 'y'
            # Add new employee to database
            newemployee = Employee(name=form.name.data, username=form.username.data, email=form.email.data, is_admin=admin)
            newemployee.set_password(form.password.data)
            db.session.add(newemployee)
            db.session.commit()
            float_hours = float(form.hours.data)
            # Based on employees working 5 days a week
            # Get hours per day
            hours = int(float_hours / 5)
            # Calculate minutes part of datetime
            minutes = int(((float_hours / 5) * 60) % 60)
            # Create datetime object to hold daily hours/time required per day
            hours = datetime(1900, 1, 1, hours, minutes)
            employeetime = EmployeeTime(employee_id = newemployee.get_id(), hours_a_week = form.hours.data,
             hours_a_day = hours.time(), flexi = '00:00:00', last_updated = datetime.now())
            db.session.add(employeetime)
            db.session.commit()
            flash('User Registered')
            return redirect(url_for('authentication.login'))
        return render_template('authentication/register.html', title='Register', form=form)
    else:
        return render_template('errors/404.html', title='Page Not Found')

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = Employee.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        # Whether user is in DB or not, flash sent message to prevent malicious use to find users
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('main.login'))
    return render_template('authentication/password_reset_request.html',
                           title='Password Reset', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = Employee.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('authentication.login'))
    return render_template('authentication/password_reset.html', form=form)
