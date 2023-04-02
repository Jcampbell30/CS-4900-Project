from flask import Blueprint, render_template, request, flash
from . import db
from .models import Users

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    email = request.form.get("email")
    psw = request.form.get("psw")

    return render_template("login.html")

@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method=='POST':
        email = request.form.get("email")
        psw1 = request.form.get("psw")
        psw2 = request.form.get("psw-repeat")

        email_exists = Users.query.filter_by(email=email).first()
        if email_exists:
            flash('Email is already in use.', category='error')
        elif psw1 != psw2:
            flash('Passwords do not match.', category='error')
        elif len(psw1) <= 20:
            flash('Passwords must be 20 characters or longer.', category='error')
        
    return render_template("signup.html")

@auth.route("/logout")
def logout():
    return "Logout"

# TBD: Check format of email to ensure it is a UTC email
def check_email(email : str):
    if "@mocs.utc.edu" in email or "@utc.edu" in email:
        return True
    return False