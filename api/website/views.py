from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .models import Template
from . import db
from datetime import datetime


views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html', user=current_user)

@login_required
@views.route('/templates', methods=['GET', 'POST'])
def templates():
#    if current_user.role == 's':
#        flash('Must be a member of faculty or a site admin to access this page.')
#        return redirect(url_for('views.home'))

    if request.method == 'POST':
        template_name = request.form['rubric_name']
        date_time = request.form['date-time']
        
        dt_obj = datetime.fromisoformat(date_time)
        mysql_date_str = dt_obj.strftime('%Y/%m/%d %H:%M:%S')

        template = Template(
            templateName=template_name,
            templateDate=mysql_date_str,
            teacherID=1,
        )
        db.session.add(template)
        db.session.commit()
    
    return render_template('template.html', user=current_user)

@views.route('/teams', methods=['GET', 'POST'])
def teams():
    return render_template('teams.html', user=current_user)

@views.route('/assignments', methods=['GET', 'POST'])
def assignments():
    return render_template('assignments.html', user=current_user)



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
