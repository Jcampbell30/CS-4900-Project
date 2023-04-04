from flask import Blueprint, render_template, request
from .models import Rubric, Team, TeamAssignment, Users
from . import db
from datetime import datetime

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html')

@views.route('/rubrics', methods=['GET', 'POST'])
def rubrics():
    if request.method == 'POST':
        rubric_name = request.form['rubric_name']
        date_time = request.form['date-time']
        
        dt_obj = datetime.fromisoformat(date_time)
        mysql_date_str = dt_obj.strftime('%Y/%m/%d %H:%M:%S')

        rubric = Rubric(
            rubricName=rubric_name,
            rubricDate=mysql_date_str,
            teacherID=1,
        )
        db.session.add(rubric)
        db.session.commit()
        
        print(date_time)
    
    return render_template('rubrics.html')

@views.route('/teams', methods=['GET', 'POST'])
def teams():
    if request.method == 'POST':
        team_name = request.form['createTeam']
        team = Team(teamName= team_name, teacherID =1)
        db.session.add(team)
        db.session.commit()

    sql = Team.query.filter_by(teacherID = 1).all()
    print(sql)
    teams = db.session.query(Team.teamName).all()
    teams = [team[0] for team in teams]


    # When the form is submitted with GET method
    if request.method == 'GET':
    # Get the teamName from the form
        team_name = request.args.get('teamID')
        #print team_name for debugging purposes
        print(team_name)
    
    # Query the Team table to find the team with the matching name
        team = db.session.query(Team).filter_by(teamName=team_name).first()
    # Print the team object for debugging purposes
        print(team)
    
    # If a team was found
        if team:
            # Get the teamID from the team object
            team_id = team.teamID
            # Get the studentID from the form / which is the name in the drop down list
            student = request.args.get('studentID')
            #query the db to see if the user exists
            user = db.session.query(Users).filter_by(userLastName=student).first()
            #make the user_id variable the users ID
            user_id = user.userID
            # Create a new TeamAssignment object with the teamID and userID
            team_assignment = TeamAssignment(teamID=team_id, userID=user_id)
            # Add the new TeamAssignment to the database and commit the transaction
            db.session.add(team_assignment)
            db.session.commit()
    # Query the Users table to get a list of all the student last names
    students = db.session.query(Users.userLastName).all()
    # Extract the student last names from the query results
    students = [student[0] for student in students]
    # Render the teams.html template and pass in the teams and students variables
    return render_template('teams.html', teams=teams, students=students)

@views.route('/assignments', methods=['GET', 'POST'])
def assignments():
    return render_template("assignments.html")  # Render the assignments.html template

@views.route("/faculty", methods=['GET', 'POST'])  # Define a route for the faculty page
def faculty():
    return render_template("faculty.html")  # Render the faculty.html template
