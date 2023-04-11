from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import Users
import hashlib, os, base64, re

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        psw = request.form.get('psw')

        user = Users.query.filter_by(email=email).first()

        if user:
            if check_hash(psw, user.salt, user.password):
                flash('Login was successful!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template('login.html', user=current_user)

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method=='POST':
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        email = request.form.get('email')
        print(email)
        psw1 = request.form.get('psw')
        psw2 = request.form.get('psw-repeat')

        email_exists = Users.query.filter_by(email=email).first()
        
        if email_exists:
            flash('Email is already in use.', category='error')
        elif not check_email(email):
            flash('Email is not a UTC email.', category='error')
        elif psw1 != psw2:
            flash('Passwords do not match.', category='error')
        elif len(psw1) < 9:
            flash('Passwords must be 9 characters or longer.', category='error')
        elif not verify_psw_rules(psw1):
            flash('Passwords must contain one of each of the following: An uppercase letter, a lowercase letter, a number, and a special character.')
        else:
            salted_psw = salt_and_hash(psw1)
            user = Users(
                userFirstName=firstName,
                userLastName=lastName,
                email=email,
                password=salted_psw[1],
                salt=str(salted_psw[0]),
                role='s')
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            flash('User created!')
            return redirect(url_for('views.home'))
        
    return render_template('signup.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful!', category='success')
    return redirect(url_for('views.home'))

def check_email(email : str):
    if '@mocs.utc.edu' in email:
        return True
    elif '@utc.edu' in email:
        return True
    return False

def verify_psw_rules(psw:str):
    pattern = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$')
    if re.search(pattern, psw):
        return True
    return False

def salt_and_hash(psw:str):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', psw.encode('utf-8'), salt, 10)
    salt_b64 = base64.b64encode(salt).decode('utf-8')
    key_b64 = base64.b64encode(key).decode('utf-8')
    return [salt_b64, key_b64]

def check_hash(psw:str, salt:str, hashed_psw:str) -> bool:
    b_salt = base64.b64decode(salt)
    b_hashed_psw = base64.b64decode(hashed_psw)
    key = hashlib.pbkdf2_hmac('sha256', psw.encode('utf-8'), b_salt, 10)
    return key == b_hashed_psw