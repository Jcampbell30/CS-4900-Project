CREATE DATABASE peer_db;

CREATE TABLE users (
  userID INT NOT NULL AUTO_INCREMENT,
  userFirstName VARCHAR(50),
  userLastName VARCHAR(50),
  email VARCHAR(100),
  password VARCHAR(150),
  salt VARCHAR(50),
  role VARCHAR(50),
  PRIMARY KEY (userID),
  UNIQUE (email)
);

CREATE TABLE course (
  courseID INT NOT NULL AUTO_INCREMENT,
  courseName VARCHAR(50),
  teacherID INT,
  FOREIGN KEY (teacherID) REFERENCES users(userID),
  PRIMARY KEY (courseID)
);

CREATE TABLE team (
  teamID INT NOT NULL AUTO_INCREMENT,
  teamName VARCHAR(50),
  courseID INT,
  FOREIGN KEY (courseID) REFERENCES course(courseID),
  PRIMARY KEY (teamID)
);

CREATE TABLE template (
  templateID INT NOT NULL AUTO_INCREMENT,
  templateName VARCHAR(50),
  templateDate VARCHAR(50),
  teacherID INT,
  gradingScale INT,
  numberQuestions INT,
  FOREIGN KEY (teacherID) REFERENCES users(userID),
  PRIMARY KEY (templateID)
);

CREATE TABLE question (
  questionID INT NOT NULL AUTO_INCREMENT,
  questionDesc VARCHAR(250),
  templateID INT,
  FOREIGN KEY (templateID) REFERENCES template(templateID),
  PRIMARY KEY (questionID)
);

CREATE TABLE teamAssignment (
  teamAssignmentID INT NOT NULL AUTO_INCREMENT,
  teamID INT,
  userID INT,
  FOREIGN KEY (teamID) REFERENCES team(teamID),
  FOREIGN KEY (userID) REFERENCES users(userID),
  PRIMARY KEY (teamAssignmentID)
);

CREATE TABLE templateAssignment (
  templateAssignmentID INT NOT NULL AUTO_INCREMENT,
  templateID INT,
  teamID INT,
  gradingScale INT,
  numberQuestions INT,
  FOREIGN KEY (templateID) REFERENCES team(teamID),
  PRIMARY KEY (templateAssignmentID)
);

CREATE TABLE studentAssignment(
  studentAssignmentID INT NOT NULL AUTO_INCREMENT,
  studentID INT,
  courseID INT,
  FOREIGN KEY (studentID) REFERENCES users(userID),
  FOREIGN KEY (courseID) REFERENCES course(courseID),
  PRIMARY KEY (studentAssignmentID)
);