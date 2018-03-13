from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app.email import send_password_reset_email
from datetime import datetime, timedelta, date, time
from app import app, db
from app.forms import LoginForm, RegisterEmployeeForm, EditProfileForm, ClockForm, ResetPasswordRequestForm, PasswordResetForm
from app.models import Employee, TimeRecord

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = ClockForm()
    if form.validate_on_submit():
        time_record = TimeRecord(employee_id='', date='')
        time_fmt = '%H:%M:%S'
        date_fmt = '%Y-%m-%d'
        user = Employee.query.filter_by(username=current_user.username).first()
        tr = TimeRecord.query.filter_by(employee_id=user.employee_id).all()
        today = datetime.strptime(str(datetime.today()), "%Y-%m-%d %H:%M:%S.%f")
        for row in tr:
            if datetime.strptime(str(row.date), date_fmt) == datetime.strptime(
            datetime.strftime(today, date_fmt), date_fmt):
                time_record = row
        if time_record.employee_id != '':
            if form.start_time.data:
                time_record.start_time = form.start_time.data
            if form.break_time.data:
                time_record.break_time = form.break_time.data
            if form.end_time.data:
                time_record.end_time = form.end_time.data
            shift = datetime.strptime(str(form.end_time.data), time_fmt) - datetime.strptime(str(form.break_time.data), time_fmt)
            start = datetime.combine(date.min, form.start_time.data) - datetime.min
            worked = shift - start
            time_record.time_worked = worked
            db.session.commit()
            flash('Clock time recorded')
        else:
            shift = datetime.strptime(str(form.end_time.data), time_fmt) - datetime.strptime(str(form.break_time.data), time_fmt)
            start = datetime.combine(date.min, form.start_time.data) - datetime.min
            worked = shift - start
            time = TimeRecord(employee_id=user.employee_id, date=datetime.today(), start_time=form.start_time.data,
                break_time=form.break_time.data, end_time=form.end_time.data, time_worked=worked)
            db.session.add(time)
            db.session.commit()
            flash('Clock time recorded')
        return redirect(url_for('index'))
    return render_template("index.html", title='Home Page', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    #if user is already logged in, redirect to index page (dont show login form again)
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(username=form.username.data).first()
        if employee is None or not employee.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(employee, remember=form.remember_me.data)
        next_page = request.args.get('next')
        #check netloc to ensure url is relative to prevent redirection to external site
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterEmployeeForm()
    if form.validate_on_submit():
        #if this is the first registered user, give them admin priveldges
        is_first_user = len(Employee.query.all())
        admin = 'n'
        if is_first_user == 0:
            admin = 'y'
        newemployee = Employee(name=form.name.data, username=form.username.data, email=form.email.data, is_admin=admin)
        newemployee.set_password(form.password.data)
        db.session.add(newemployee)
        db.session.commit()
        flash('User Registered')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = Employee.query.filter_by(username=username).first_or_404()
# Do not allow employee's to access each others accounts, restrict this activity to admin accounts.
    if user.username != current_user.username:
        if current_user.is_admin == 'y':
            return render_template('profile.html', user=user)
        else:
            return redirect(url_for('index'))
    else:
        return render_template('profile.html', user=user)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
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
        return redirect(url_for('edit_profile'))
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

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = Employee.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('password_reset_request.html',
                           title='Password Reset', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = Employee.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('password_reset.html', form=form)
