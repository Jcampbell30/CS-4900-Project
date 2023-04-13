from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .models import Users, Template, Course, StudentAssignment, TemplateAssignment, Question
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
        flash(f'The {template_name} template was created successfully.', category='success')
        return redirect(url_for('views.faculty'))
    return render_template('template.html', user=current_user)

@views.route("/questions", methods = ['GET','POST'])
def questions():
    
    if current_user.role == 's':
        flash("Must not be a student")
        return redirect(url_for("views.home")) 
    if 'templateSelection' in request.form:
        template_id = request.form['templateSelection']
    else:
        template_id = request.form.get('template_id')  
    template = Template.query.filter_by(templateID=template_id).first()
    question = Question.query.filter_by(templateID=template_id).all()
    if len(question) == 0:
        created = False
        if request.method=='POST':
            if 'templateSelection' in request.form:
                template_id = request.form['templateSelection']
            else:
                template_id = request.form['template_id']
            template = Template.query.filter_by(templateID=template_id).first()
            num_questions = template.numberQuestions
            template_name = template.templateName
        
            if 'templateSelection' not in request.form:
                for i in range(num_questions):
                    question_description = request.form.get("question{}".format(i))
                    question = Question(questionDesc = question_description, templateID=template_id)
                    db.session.add(question)
                    db.session.commit()
                if num_questions > 0:
                    flash(f'Questions added successfully to the {template_name} template.', category='success')
                    return redirect(url_for('views.questions', template_id=template_id))
            
            return render_template("questions.html", user = current_user, num_questions = num_questions,template_name = template_name, template_id=template_id)
    else:
        created = True
        template = Template.query.filter_by(templateID=template_id).first()
        template_name = template.templateName
        my_questions = []
        num_questions = len(question)
        for i in range(len(question)):
            my_questions.append(question[i].questionDesc)
        return render_template("questions.html", user = current_user, template_id=template_id, my_questions=my_questions, num_questions=num_questions,created = created, template_name = template.templateName)
        
    return redirect(url_for('views.faculty'))


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
        if 'courseSelection' in request.form:
            course_id = request.form['courseSelection']
        else:
            course_id = request.form['course_id']
    
        course_selection = Course.query.filter_by(courseID = course_id).first()
        course_assignments = StudentAssignment.query.filter_by(courseID = course_id).all()
        student_ids = []
        for student in course_assignments:
            student_ids.append(student.studentID)
        course_students = Users.query.filter(Users.userID.in_(student_ids)).all()

        if 'student_id' in request.form:
            utc_id = request.form['student_id'].lower()
            student_email = f'{utc_id}@mocs.utc.edu'
            student = Users.query.filter_by(email=student_email).first()
            if student in course_students:
                flash('Student already in class!', category='error')
            else:
                sa = StudentAssignment(
                    studentID = student.userID,
                    courseID = course_id
                )
                db.session.add(sa)
                db.session.commit()
                flash('Student successfully added!', category='success')

        return render_template('course.html', user=current_user, course=course_selection, students=course_students)

    flash('Must select a course from admin page!', category='error')
    return redirect(url_for('views.admin'))


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

@views.route('/permissions')
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
