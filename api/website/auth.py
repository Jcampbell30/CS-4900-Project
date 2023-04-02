from flask import Blueprint, render_template, request

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    return "Login"

@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    email = request.form.get("email")
    psw1 = request.form.get("psw")
    psw2 = request.form.get("psw-repeat")

    return render_template("index.html")

@auth.route("/logout")
def logout():
    return "Logout"