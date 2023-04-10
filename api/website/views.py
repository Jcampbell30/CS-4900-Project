from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .models import Users, Template, Course, StudentAssignment, TemplateAssignment, Question, QuestionAssignment
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

    my_templates = db.session.query(Users.userID, Template.templateName, Template.numberQuestions).\
                    join(Template).all()
    if len(my_templates) < 1:
        my_templates = [(1,"View Template",3),(1, "View Template", 3)]
    i = 0
    print(len(my_templates))
    template_names = []
    while i < len(my_templates):
        template_names.append(my_templates[i][1])
        i+=1
    
    print(template_names)
    
    return render_template('faculty.html', user=current_user,template_names = template_names)

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
    teacher_templates = db.session.query(Users.userID, Template.templateName, Template.numberQuestions, Template.templateID).\
                    join(Template).all()
    num_questions = teacher_templates[0][2]
    template_name = teacher_templates[0][1]
    template_name = template_name.upper()
    stmt = db.session.query(QuestionAssignment.questionAssignmentID)\
                .join(Question, Question.questionID == QuestionAssignment.questionID)\
                .join(Template, Template.templateID == Question.questionID)\
                .filter(Template.templateID == TemplateAssignment.templateID)\
                .with_entities(QuestionAssignment.questionAssignmentID).all()
    print(f"the sql statement: {stmt}")
    print(f"number of questions: {num_questions}")
    for i in range (num_questions):
        print(i)
    print(f"The teacher templates: {teacher_templates},and the number of questions:  {num_questions}")
    if request.method == 'POST':
        for i in range(num_questions):
            question_description = request.form.get("question{}".format(i+1))
            print(f"question_description is: {question_description}")
            question = Question(questionDesc = question_description)
            template_id = teacher_templates[0][3]
            q_a = QuestionAssignment(templateID = template_id,questionID = question.questionID )
            print(template_id)
            db.session.add(q_a)
            db.session.add(question)
            db.session.commit()
        

    return render_template("questions.html", user = current_user, num_questions = num_questions,template_name = template_name)

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
