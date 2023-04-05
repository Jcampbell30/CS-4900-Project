from . import db
from flask_login import UserMixin

###############
# Data tables #
###############
class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    userID = db.Column(db.Integer, primary_key=True)
    userFirstName = db.Column(db.String(50))
    userLastName = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(150))
    salt = db.Column(db.String(50))
    role = db.Column(db.String(50))

    def get_id(self):
        return self.userID

class Course(db.Model):
    __tablename__ = 'course'
    courseID = db.Column(db.Integer, primary_key=True)
    courseName = db.Column(db.String(50))
    teacherID = db.Column(db.Integer, db.ForeignKey('users.userID'))

class Team(db.Model):
    __tablename__ = 'team'
    teamID = db.Column(db.Integer, primary_key=True)
    teamName = db.Column(db.String(50))
    courseID = db.Column(db.Integer, db.ForeignKey('course.courseID'))

class Template(db.Model):
    __tablename__ = 'template'
    templateID = db.Column(db.Integer, primary_key=True)
    templateName = db.Column(db.String(50))
    templateDate = db.Column(db.String(50))
    teacherID = db.Column(db.Integer, db.ForeignKey('users.userID'))

class Question(db.Model):
    __tablename__ = 'question'
    questionID = db.Column(db.Integer, primary_key=True)
    questionDesc = db.Column(db.String(250))

##################
# Relation table #
##################
class TeamAssignment(db.Model):
    __tablename__ = 'teamAssignment'
    teamAssignmentID = db.Column(db.Integer, primary_key=True)
    teamID = db.Column(db.Integer, db.ForeignKey('team.teamID'))
    userID = db.Column(db.Integer, db.ForeignKey('users.userID'))

class TemplateAssignment(db.Model):
    __tablename__ = 'templateAssignment'
    templateAssignmentID = db.Column(db.Integer, primary_key=True)
    templateID = db.Column(db.Integer, db.ForeignKey('template.templateID'))
    teamID = db.Column(db.Integer, db.ForeignKey('team.teamID'))

class QuestionAssignment(db.Model):
    __tablename__ = 'questionAssignment'
    questionAssignmentID = db.Column(db.Integer, primary_key=True)
    templateID = db.Column(db.Integer, db.ForeignKey('template.templateID'))
    questionID = db.Column(db.Integer, db.ForeignKey('question.questionID'))

class StudentAssignment(db.Model):
    __tablename__ = 'studentAssignment'
    studentAssignmentID = db.Column(db.Integer, primary_key=True)
    studentID = db.Column(db.Integer, db.ForeignKey('users.userID'))
    courseID = db.Column(db.Integer, db.ForeignKey('course.courseID'))