from flask import Blueprint, render_template
from flask import request

views = Blueprint("views", __name__)

@views.route("/")
def home():
    return render_template("home.html")

@views.route("/rubrics", methods=['GET', 'POST'])
def rubrics():

    return render_template("rubrics.html")

@views.route("/teams", methods=['GET', 'POST'])
def teams():
    return render_template("teams.html")

@views.route("/assignments", methods=['GET', 'POST'])
def assignments():
    return render_template("assignments.html")