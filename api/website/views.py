from flask import Blueprint, render_template, request  # Import the necessary modules

views = Blueprint("views", __name__)  # Define the blueprint for this module
 # Declare `rows` as a global variable
rows = [{}]       # Initialize `rows` as a list containing an empty dictionary
@views.route("/")  # Define a route for the home page
def home():
    return render_template("home.html")  # Render the home.html template

@views.route("/rubrics", methods=['GET','POST'])  # Define a route for the rubrics page
def rubrics():
    if request.method == "POST":  # If the request method is POST (i.e., a form has been submitted)
        name = request.form['name']  # Get the value of the "name" field from the form
        age = request.form['age']  # Get the value of the "age" field from the form
        new_row = {'name': name, 'age': age}  # Create a new dictionary containing the name and age
        rows.append(new_row)  # Append the new row to the `rows` list
    if request.method == "GET":
        rows.clear()
    return render_template("rubrics.html",rows = rows)  # Render the rubrics.html template with the `rows` variable passed as a parameter

@views.route("/teams", methods=['GET', 'POST'])  # Define a route for the teams page
def teams():
    return render_template("teams.html")  # Render the teams.html template

@views.route("/assignments", methods=['GET', 'POST'])  # Define a route for the assignments page
def assignments():
    return render_template("assignments.html")  # Render the assignments.html template