<<<<<<< HEAD
from flask import Blueprint, render_template, request
from .models import Rubric, Team, TeamAssignment, Users
=======
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .models import Users, Template, Course, StudentAssignment, TemplateAssignment, Question, QuestionAssignment
>>>>>>> e08e9f8a70027cbb3f6ca70e863f11e1310f6c85
from . import db
from datetime import datetime

views = Blueprint('views', __name__)

##################
# EVERYONE VIEWS #
##################

@views.route('/')
def home():
    return render_template('home.html', user=current_user)

#################
# STUDENT VIEWS #
#################

@views.route('/assignments', methods=['GET', 'POST'])
@login_required
def assignments():
    return render_template('assignments.html', user=current_user)

#################
# FACULTY VIEWS #
#################

@views.route('/faculty', methods=['GET', 'POST'])
@login_required
def faculty():
    if current_user.role == 's':
        flash('Must be a member of faculty or a site admin to access this page.', category='error')
        return redirect(url_for('views.home'))

    my_templates = Template.query.filter_by(teacherID=current_user.userID).all()
    
    return render_template('faculty.html', user=current_user,templates=my_templates)

@views.route('/templates', methods=['GET', 'POST'])
@login_required
def templates():
 
    if current_user.role == 's':
        flash('Must be a member of faculty or a site admin to access this page.', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        template_name = request.form['rubric_name']
        date_time = request.form['date-time']
        grading_scale = request.form['grading_scale']
        num_questions = request.form['num_questions']
        dt_obj = datetime.fromisoformat(date_time)
        mysql_date_str = dt_obj.strftime('%Y/%m/%d %H:%M:%S')

        template = Template(
            templateName=template_name,
            templateDate=mysql_date_str,
            teacherID= current_user.userID,
            gradingScale = grading_scale,
            numberQuestions = num_questions
        )
        db.session.add(template)
        db.session.commit()
        
    return render_template('template.html', user=current_user)

@views.route("/questions", methods = ['GET','POST'])
def questions():
    if current_user.role == 's':
        flash("Must not be a student")
        return redirect(url_for("views.home"))

    if request.method=='POST':
        if 'templateSelection' in request.form:
            template_id = request.form['templateSelection']
        else:
            template_id = request.form['template_id']
        template = Template.query.filter_by(templateID=template_id).first()
        num_questions = template.numberQuestions
        template_name = template.templateName
        if 'templateSelection' not in request.form:
            print(f"number of questions: {num_questions}")
            for i in range (num_questions):
                print(i)
            for i in range(num_questions):
                question_description = request.form.get("question{}".format(i+1))
                print(f"question_description is: {question_description}")
                question = Question(questionDesc = question_description)
                db.session.add(question)
                db.session.commit()
                print(f'Question ID: {question.questionID}')
                template_id = template.templateID
                q_a = QuestionAssignment(templateID = template_id, questionID = question.questionID )
                print(template_id)
                db.session.add(q_a)
                db.session.commit()
        
        return render_template("questions.html", user = current_user, num_questions = num_questions,template_name = template_name, template_id=template_id)
    flash('Please pick a template from the list of templates.', category='error')
    return redirect(url_for('views.faculty'))

    created = False #boolean to check if the assignments have been saved to the template

    """
    try and return the questionsAssignmentID from the templateAssignmentID
    if I can't return it then go to create view else I got to a table view of the questions in the template
    
    """
    
  
"""
    IF not created: 
        create view. 
"""
@views.route('/teams', methods=['GET', 'POST'])
@login_required
def teams():
<<<<<<< HEAD
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
=======
    return render_template('teams.html', user=current_user)

################
# ADMIN VIEWS  #
################

@views.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.role != 'a':
        flash('Must be a site admin to access this page.', category='error')
        return redirect(url_for('views.home'))

    all_courses = Course.query.all()

    return render_template('admin.html', user=current_user, courses=all_courses)

@views.route('/course', methods=['GET', 'POST'])
@login_required
def course():
    if current_user.role != 'a':
        flash('Must be a site admin to access this page.', category='error')
        return redirect(url_for('views.home'))
    
    if request.method=='POST':
        if request.form['courseSelection']:
            course_id = request.form['courseSelection']
            course_selection = Course.query.filter_by(courseID = course_id).first()
            course_students = StudentAssignment.query.filter_by(courseID = course_id).all()

            return render_template('course.html', user=current_user, course=course_selection, students=course_students)


@views.route('/create-course', methods=['GET', 'POST'])
@login_required
def create_course():
    if current_user.role != 'a':
        flash('Must be a site admin to access this page.', category='error')
        return redirect(url_for('views.home'))
    
    if request.method == 'POST':
        name = request.form['courseName']
        id = request.form['assignedFaculty']

        course_exists = Course.query.filter_by(courseName=name).first()
        if course_exists:
            flash('Course name already in use.', category='error')
        else:
            course = Course(
                courseName = name,
                teacherID = id
            )
            db.session.add(course)
            db.session.commit()
            flash('Course created successfully!', category='success')
    
    all_faculty = Users.query.filter_by(role='f').all()

    return render_template('create-course.html', user=current_user, faculty=all_faculty)

@views.route('/permissions', methods=['GET', 'POST'])
@login_required
def permissions():
    if current_user.role != 'a':
        flash('Must be a site admin to access this page.', category='error')
        return redirect(url_for('views.home'))
    
    if request.method=='POST':
        new_faculty = Users.query.filter_by(userID=request.form['email_selection']).first()
        print()
        new_faculty.role = 'f'
        db.session.commit()
        flash('New faculty added!', category='success')

    all_faculty = Users.query.filter_by(role='f').all()

    valid_emails = Users.query.filter(Users.email.contains('@utc.edu')).all()
    
    return render_template('permissions.html', user=current_user, faculty=all_faculty, valid_emails=valid_emails)


##########################
# DELETE BEFORE DELIVERY #
##########################
@views.route('/make-student')
@login_required
def make_student():
    current_user.role = 's'
    db.session.commit()
    flash('You were made a student.', category='success')
    return redirect(url_for('views.home'))

@views.route('/make-faculty')
@login_required
def make_faculty():
    current_user.role = 'f'
    db.session.commit()
    flash('You were made faculty.', category='success')
    return redirect(url_for('views.home'))

@views.route('/make-admin')
@login_required
def make_admin():
    current_user.role = 'a'
    db.session.commit()
    flash('You were made an admin.', category='success')
    return redirect(url_for('views.home'))
>>>>>>> e08e9f8a70027cbb3f6ca70e863f11e1310f6c85
