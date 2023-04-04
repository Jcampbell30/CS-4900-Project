from flask import Blueprint, render_template, request  # Import the necessary modules
from .models import Rubric
import requests
from flask import flash
from . import db
from datetime import datetime


views = Blueprint("views", __name__)  # Define the blueprint for this module
 # Declare `rows` as a global variable
 #       # Initialize `rows` as a list containing an empty dictionary
@views.route("/")  # Define a route for the home page
def home():
    return render_template("home.html")  # Render the home.html template

@views.route("/rubrics", methods=['GET', 'POST'])
def rubrics():
    if request.method == "POST":
        rubric_name = request.form['rubric_name']
        date_time = request.form['date-time']
        # Send data to API endpoint
        dt_obj = datetime.fromisoformat(date_time)

# Format datetime object to MySQL format
        mysql_date_str = dt_obj.strftime('%Y/%m/%d %H:%M:%S')

        rubric = Rubric(
            rubricName=rubric_name,
            rubricDate=mysql_date_str,
            teacherID=1,
            )
        db.session.add(rubric)
        db.session.commit()
        # Check if request was successful
        print(date_time)
        
    return render_template("rubrics.html")

@views.route("/teams", methods=['GET', 'POST'])  # Define a route for the teams page
def teams():
    return render_template("teams.html")  # Render the teams.html template

@views.route("/assignments", methods=['GET', 'POST'])  # Define a route for the assignments page
def assignments():
    return render_template("assignments.html")  # Render the assignments.html template