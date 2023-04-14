from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .models import Users, Template, Course, StudentAssignment, TemplateAssignment, Question, TeamAssignment, Team
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

@views.route('/peer-review/<int:id>', methods=['GET', 'POST'])
@login_required
def peer_review(id):
    if current_user.role == 's':
        flash('Must be a student to access peer reviews!', category='error')
        return redirect(url_for('views.home'))

    template = Template.query.get_or_404(id)
    course = Course.query.filter_by()


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
    my_courses =  Course.query.filter_by(teacherID=current_user.userID).all()

    if request.method == 'POST':
        if 'course_selection' in request.form:
            return redirect(url_for('views.teams', course_id=request.form['course_selection']))

    return render_template('faculty.html', user=current_user,templates=my_templates,courses=my_courses)

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

# Team Management Page
@views.route('/teams/<int:course_id>', methods=['GET', 'POST'])
@login_required
def teams(course_id):
    if current_user.role == 's':
        flash('Must be a member of faculty or a site admin to access this page.', category='error')
        return redirect(url_for('views.home'))
    
    course = Course.query.get_or_404(course_id)

    if course.teacherID != current_user.userID:
        flash('You do not have permission to view this course!', category='error')
        return redirect(url_for('views.faculty'))
    

    if request.method == 'POST':
        if 'createTeam' in request.form:
            teamName = request.form['createTeam']
            team = Team(teamName=teamName, courseID=course.courseID)
            db.session.add(team)
            db.session.commit()
            flash(f'The {teamName} team was created successfully.', category='success')
        elif 'teamID' in request.form:
            try:
                team_id = request.form['teamID']
                print(f"team_id = {team_id}")
                already_assigned = TeamAssignment.query.filter_by(teamID=team_id).filter_by(userID=request.form['studentID']).first()
                print (already_assigned)
                if already_assigned:
                    flash('Student already assigned to this team!', category='error')
                else:
                    team = TeamAssignment(teamID=team_id, userID=request.form['studentID'])
                    db.session.add(team)
                    db.session.commit()
                    flash('Student assigned to team!', category='success')
            except Exception as e:
                print(e)
    
    print(current_user.userID)
    assigned_ids = StudentAssignment.query.filter_by(courseID=course_id)

    all_students = Users.query.filter_by(role='s').all()
    
    teams=Team.query.filter_by(courseID=course.courseID).all()
    print(teams)
    return render_template('teams.html', user=current_user, course=course, students=all_students, teams=teams)

# Individual team page
@views.route('/team/<int:id>', methods=['GET', 'POST'])
@login_required
def team(id):
    pass

################
# ADMIN VIEWS  #
################

@views.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.role != 'a':
        flash('Must be a site admin to access this page.', category='error')
        return redirect(url_for('views.home'))

    all_my_courses = Course.query.all()

    return render_template('admin.html', user=current_user, my_courses=all_my_courses)

@views.route('/course/<int:id>', methods=['GET', 'POST'])
@login_required
def course(id):
    if current_user.role != 'a':
        flash('Must be a site admin to access this page.', category='error')
        return redirect(url_for('views.home'))
    
    course=Course.query.get_or_404(id)

    course_assignments = StudentAssignment.query.filter_by(courseID = id).all()
    student_ids = []
    for student in course_assignments:
        student_ids.append(student.studentID)
    course_students = Users.query.filter(Users.userID.in_(student_ids)).all()

    if request.method == 'POST':
        if 'student_id' in request.form:
            utc_id = request.form['student_id'].lower()
            student_email = f'{utc_id}@mocs.utc.edu'
            student = Users.query.filter_by(email=student_email).first()
            if student in course_students:
                flash('Student already in class!', category='error')
            else:
                sa = StudentAssignment(
                    studentID = student.userID,
                    courseID = course.courseID
                )
                db.session.add(sa)
                db.session.commit()
                flash('Student successfully added!', category='success')
        
    return render_template('course.html', user=current_user, course=course, students=course_students)

@views.route('/remove-student/<int:course_id>/<int:user_id>', methods=['GET', 'POST'])
@login_required
def remove_student(course_id, user_id):
    if current_user.role != 'a':
        flash('Must be a site admin to access this page.', category='error')
        return redirect(url_for('views.home'))
    
    try:
        course=Course.query.filter_by(courseID=course_id).first()
    except:
        flash('Invalid course!', category='error')
        return redirect(url_for('views.admin'))

    try:
        sa_to_remove = StudentAssignment.query.filter_by(studentID=user_id).filter_by(courseID=course_id).first()
        print(sa_to_remove.studentID)
        db.session.delete(sa_to_remove)
        db.session.commit()
        flash('Student unassigned to course!', category='success')
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        flash('Student not assigned to course!', category='error')
    return redirect(url_for('views.course', id=course.courseID))

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
    

    all_faculty = Users.query.filter(Users.role.in_(['f', 'a'])).all()

    return render_template('create-course.html', user=current_user, faculty=all_faculty)

@views.route('/permissions', methods=['GET', 'POST'])
@login_required
def permissions():
    if current_user.role != 'a':
        flash('Must be a site admin to access this page.', category='error')
        return redirect(url_for('views.home'))
    
    if request.method=='POST':
        if 'demote' in request.form:
            user = Users.query.filter_by(userID=request.form['demote']).first()
            user.role = 's'
            db.session.commit()
            flash('Faculty demoted!', category='success')
        elif 'email_selection' in request.form:
            new_faculty = Users.query.filter_by(userID=request.form['email_selection']).first()
            print()
            new_faculty.role = 'f'
            db.session.commit()
            flash('New faculty added!', category='success')

    all_faculty = Users.query.filter_by(role='f').all()
    valid_emails = Users.query.filter(Users.email.contains('@utc.edu')).all()
    valid_emails.remove(current_user)
    for f in all_faculty:
        valid_emails.remove(f)

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
