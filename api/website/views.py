from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .models import Users, Template, Course, StudentAssignment, TemplateAssignment, Question, TeamAssignment, Team, StudentGrades
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
    # Check if current user is permitted to use page.
    if current_user.role != 's':
        flash('Must be a student to access peer reviews!', category='error')
        return redirect(url_for('views.home'))
    
    # Redirect to a peer review if they submitted a valid form.
    if request.method=='POST':
        if 'course_select' in request.form:
            template_assignment = TemplateAssignment.query.filter_by(courseID=request.form['course_select']).first()
            template = Template.query.get(template_assignment.templateID)
            return redirect(url_for('views.peer_review', course_id=request.form['course_select'], template_id=template.templateID))

    # Get a list of the current user's assigned courses.
    course_assignments=StudentAssignment.query.filter_by(studentID=current_user.userID).all()
    courses=[]
    for course in course_assignments:
        courses.append(Course.query.get(course.courseID))

    return render_template('assignments.html', user=current_user, courses=courses, teams=teams)

@views.route('/peer-review/<int:course_id>/<int:template_id>', methods=['GET', 'POST'])
@login_required
def peer_review(course_id, template_id):
    # Check if current user is permitted to use page.
    if current_user.role != 's':
        flash('Must be a student to access peer reviews!', category='error')
        return redirect(url_for('views.home'))

    # Get template and course object or error out with a 404 page.
    template = Template.query.get_or_404(template_id)
    course = Course.query.get_or_404(course_id)

    # Get a template assignment and ensure the template is assigned to the course.
    template_assignment = TemplateAssignment.query.filter_by(templateID=template_id).filter_by(courseID=course_id).first()
    if not template_assignment:
        flash('This template is not assigned to this course!', category='error')
        return redirect(url_for('views.assignments'))

    # Get a student assignment and ensure the student is assigned to the course
    course_student=StudentAssignment.query.filter_by(courseID=course.courseID).filter_by(studentID=current_user.userID).first()
    if not course_student:
        flash('You are not assigned to this course!', category='error')
        return redirect(url_for('views.assignments'))
    
    # Get the current user their team, if assigned to one.
    team_assignments=TeamAssignment.query.filter_by(userID=current_user.userID).all()
    team = None
    for ta in team_assignments:
        team = Team.query.filter_by(teamID=ta.teamID).first()
        if team.courseID == course_id:
            break
        team = None
    if team == None:
        flash('You are not assigned to a team!', category='error')
        return redirect(url_for('views.assignments'))

    # Get the current user's teammates
    team_member_assignments=TeamAssignment.query.filter_by(teamID=team.teamID).all()
    team_members = []
    for member in team_member_assignments:
        if member.userID == current_user.userID:
            continue
        team_members.append(Users.query.get(member.userID))

    # Grabs questions for template
    questions = Question.query.filter_by(templateID=template_id).all()

    # Check if they already submitted this peer review.
    alreadySubmitted = StudentGrades.query.filter_by(studentID=current_user.userID).filter_by(targetID=current_user.userID).filter_by(questionID=questions[0].questionID).first()
    if alreadySubmitted:
        flash('You have already completed this peer review!', category='error')
        return redirect(url_for('views.assignments'))

    # If form submitted, service the submission
    if request.method=='POST':
        grades=[]
        for question in questions:
            grades.append(StudentGrades(
                studentID=current_user.userID,
                targetID=current_user.userID,
                questionID=question.questionID,
                templateID=template_id,
                grade=request.form[f'{current_user.userID}_{question.questionID}']
            ))
            for tm in team_members:
                grades.append(StudentGrades(
                    studentID=current_user.userID,
                    targetID=tm.userID,
                    questionID=question.questionID,
                    templateID=template_id,
                    grade=request.form[f'{tm.userID}_{question.questionID}']
                ))
        for grade in grades:
            db.session.add(grade)
        db.session.commit()
        flash('Successfully submitted peer review!', category='success')
        return redirect(url_for('views.assignments'))

    return render_template('peer-review.html', user=current_user, course=course, template=template, team=team, team_members=team_members, questions=questions)


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
        if 'template_selection' in request.form:
            template = Template.query.get_or_404(request.form['template_selection'])
            course = Course.query.get_or_404(request.form['course_selection'])
            temp_assigned = TemplateAssignment.query.filter_by(templateID=template.templateID).filter_by(courseID=course.courseID).first()
            if temp_assigned:
                flash('Template already assigned to class!', category='error')
                return render_template('faculty.html', user=current_user,templates=my_templates,courses=my_courses)  
            temp_assign = TemplateAssignment(templateID=template.templateID, courseID=course.courseID)
            db.session.add(temp_assign)
            db.session.commit()
            flash('Template assigned to course!', category='success')
        else:
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
            return redirect(url_for('views.team', course_id=course_id, team_id=request.form['teamID']))
        elif 'templateID' in request.form:
            return redirect(url_for('views.results', course_id=course_id, template_id=request.form['templateID']))
    assigned_ids = StudentAssignment.query.filter_by(courseID=course_id)

    all_students = Users.query.filter_by(role='s').all()
    
    teams=Team.query.filter_by(courseID=course.courseID).all()
    template_assignments=TemplateAssignment.query.filter_by(courseID=course_id).all()
    templates=[]
    for t in template_assignments:
        templates.append(Template.query.get(t.templateID))
    return render_template('teams.html', user=current_user, course=course, students=all_students, teams=teams, templates=templates)

# Individual team page
@views.route('/teams/<int:course_id>/<int:team_id>', methods=['GET', 'POST'])
@login_required
def team(course_id, team_id):
    if current_user.role == 's':
        flash('Must be a member of faculty or a site admin to access this page.', category='error')
        return redirect(url_for('views.home'))
    
    course = Course.query.get_or_404(course_id)

    if course.teacherID != current_user.userID:
        flash('You do not have permission to view this course!', category='error')
        return redirect(url_for('views.faculty'))
    
    if request.method=='POST':
        if 'student_selection' in request.form:
            studentID = request.form['student_selection']
            already_assigned = TeamAssignment.query.filter_by(userID=studentID).filter_by(teamID=team_id).first()
            if already_assigned:
                flash('Student already assigned to team!', category='error')
            else:
                ta = TeamAssignment(
                    teamID=team_id,
                    userID=studentID
                )
                db.session.add(ta)
                db.session.commit()
                flash('Student successfully added to team!', category='success')

    team = Team.query.get_or_404(team_id)
    student_ids=TeamAssignment.query.filter_by(teamID=team.teamID).all()
    students=[]
    for sid in student_ids:
        student_id = sid.userID
        students.append(Users.query.get(student_id))

    course_students = StudentAssignment.query.filter_by(courseID=course_id).all()
    all_students=[]
    for s in course_students:
        all_students.append(Users.query.get(s.studentID))

    return render_template('team.html', user=current_user, course=course, team=team, students=students, all_students=all_students)

@views.route('/team/<int:team_id>/remove/<int:student_id>')
@login_required
def team_remove(team_id, student_id):
    if current_user.role == 's':
        flash('Must be a member of faculty or a site admin to access this page.', category='error')
        return redirect(url_for('views.home'))
    
    team = Team.query.get_or_404(team_id)
    course = Course.query.get_or_404(team.courseID)

    if course.teacherID != current_user.userID:
        flash('You do not have permission to modify this team!', category='error')
        return redirect(url_for('views.faculty'))
    
    ta = TeamAssignment.query.filter_by(userID=student_id).filter_by(teamID=team.teamID).first()
    if ta:
        db.session.delete(ta)
        db.session.commit()
        flash('User successfully removed', category='success')
    else:   
        flash('User not assigned to team!', category='error')
    return redirect(url_for('views.team', course_id=course.courseID, team_id=team.teamID))

@views.route('/results/<int:course_id>/<int:template_id>')
@login_required
def results(course_id, template_id):
    if current_user.role == 's':
        flash('Must be a member of faculty or a site admin to access this page.', category='error')
        return redirect(url_for('views.home'))
    
    course = Course.query.get_or_404(course_id)
    template = Template.query.get_or_404(template_id)

    if course.teacherID != current_user.userID:
        flash('You are not the assigned faculty of this course!', category='error')
        return redirect(url_for('views.faculty'))
    
    teams = Team.query.filter_by(courseID=course.courseID).all()
    questions = Question.query.filter_by(templateID=template_id).all()
    team_info = []
    for team in teams:
        team_assignments=TeamAssignment.query.filter_by(teamID=team.teamID).all()
        team_members=[]
        for assignment in team_assignments:
            team_members.append(Users.query.get(assignment.userID))
        
        members=[]
        for member in team_members:
            grades = StudentGrades.query.filter_by(templateID=template_id).filter_by(targetID=member.userID).all()
            members.append(
                ResultStudent(
                    user=member,
                    grades=getQuestionGrades(grades=grades, questions=questions),
                    final=getFinal(grades=grades, team_members=len(team_members))
                )
            )
        t = [team, members]
        team_info.append(t)

    return render_template('results.html', user=current_user, template=template, course=course, questions=questions, team_info=team_info)


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
    try:
        valid_emails.remove(current_user)
        for f in all_faculty:
            valid_emails.remove(f)
    except:
        pass

    return render_template('permissions.html', user=current_user, faculty=all_faculty, valid_emails=valid_emails)




class ResultStudent():
    def __init__(self, user:Users, grades:dict, final:float):
        self.user = user
        self.grades = grades
        self.final = final
    
    
def getFinal(grades: list, team_members:int):
    final = 0
    for grade in grades:
        final = final + grade.grade
    final = final/team_members
    return final

def getQuestionGrades(grades:list, questions:list):
    total={}
    for question in questions:
        total_grade=0
        for grade in grades:
            if grade.questionID == question.questionID:
                total_grade=total_grade+grade.grade
        total.update({f'{ question.questionID }' : total_grade} )
    return total
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
