from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegisterEmployeeForm
from app.models import Employee

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')

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
        result = len(Employee.query.all())
        admin = 'n'
        if result == 0:
            admin = 'y'
        newemployee = Employee(username=form.username.data, email=form.email.data, is_admin=admin)
        newemployee.set_password(form.password.data)
        db.session.add(newemployee)
        db.session.commit()
        flash('User Registered')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
