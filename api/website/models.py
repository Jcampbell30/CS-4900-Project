from . import db
from flask_login import UserMixin

###############
# Data tables #
###############
class Users(db.Model, UserMixin):
    __tablename__ = "users"
    userID = db.Column(db.Integer, primary_key=True)
    userFirstName = db.Column(db.String(50))
    userLastName = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(150))
    role = db.Column(db.String(50))

class Team(db.Model):
    __tablename__ = "team"
    teamID = db.Column(db.Integer, primary_key=True)
    teamName = db.Column(db.String(50))

class Rubric(db.Model):
    __tablename__ = "rubric"
    rubricID = db.Column(db.Integer, primary_key=True)

class Question(db.Model):
    __tablename__ = "question"
    questionID = db.Column(db.Integer, primary_key=True)
    questionDesc = db.Column(db.String(250))

##################
# Relation table #
##################
class TeamAssignment(db.Model):
    __tablename__ = "teamAssignment"
    teamAssignmentID = db.Column(db.Integer, primary_key=True)
    teamID = db.Column(db.Integer, db.ForeignKey('team.teamID'))
    userID = db.Column(db.Integer, db.ForeignKey('users.userID'))

class RubricAssignment(db.Model):
    __tablename__ = "rubricAssignment"
    rubricAssignmentID = db.Column(db.Integer, primary_key=True)
    rubricID = db.Column(db.Integer, db.ForeignKey("rubric.rubricID"))
    teamID = db.Column(db.Integer, db.ForeignKey("team.teamID"))

class QuestionAssignment(db.Model):
    __tablename__ = "questionAssignment"
    questionAssignmentID = db.Column(db.Integer, primary_key=True)
    rubricID = db.Column(db.Integer, db.ForeignKey("rubric.rubricID"))
    questionID = db.Column(db.Integer, db.ForeignKey("question.questionID"))