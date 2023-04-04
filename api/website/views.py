from flask import Blueprint, render_template, request
from .models import Rubric
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
    return render_template('teams.html')

@views.route('/assignments', methods=['GET', 'POST'])
def assignments():
    return render_template('assignments.html')