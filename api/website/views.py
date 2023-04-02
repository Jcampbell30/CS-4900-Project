from flask import Blueprint, render_template
from flask import request

views = Blueprint("views", __name__)

@views.route("/")
def home():
    return render_template("home.html")

@views.route("/rubrics")
def rubrics():

    return render_template("rubrics.html")

@views.route("/assignments")
def assignments():
    return render_template("assignments.html")