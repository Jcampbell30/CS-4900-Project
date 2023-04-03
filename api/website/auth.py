from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db
from .models import Users
import hashlib, secrets

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    email = request.form.get("email")
    psw = request.form.get("psw")

    return render_template("login.html")

@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method=='POST':
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        email = request.form.get("email")
        psw1 = request.form.get("psw")
        psw2 = request.form.get("psw-repeat")

        email_exists = Users.query.filter_by(email=email).first()
        
        if email_exists:
            flash('Email is already in use.', category='error')
        elif not check_email(email):
            flash('Email is not a UTC email.', category='error')
        elif psw1 != psw2:
            flash('Passwords do not match.', category='error')
        elif len(psw1) <= 9:
            flash('Passwords must be 9 characters or longer.', category='error')
        else:
            salted_psw = salt_and_hash(psw1)
            user = Users(
                userFirstName=firstName,
                userLastName=lastName,
                email=email,
                password=salted_psw[1],
                salt=salted_psw[0],
                role='s')
            db.session.add(user)
            db.session.commit()
            flash('User created!')
            return redirect(url_for('views.home'))
        
    return render_template("signup.html")

@auth.route("/logout")
def logout():
    return "Logout"

# TBD: Check format of email to ensure it is a UTC email
def check_email(email : str):
    if "@mocs.utc.edu" in email:
        return True
    elif "@utc.edu" in email:
        return True
    return False

def salt_and_hash(psw:str):
    salt = secrets.token_bytes(16)
    salted_password = salt + psw.encode('utf-8')
    hashed_password = hashlib.sha256(salted_password).hexdigest()
    return [salt, hashed_password]