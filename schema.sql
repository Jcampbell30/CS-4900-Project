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

CREATE TABLE team (
  teamID INT NOT NULL AUTO_INCREMENT,
  teamName VARCHAR(50),
  teacherID INT,
  FOREIGN KEY (teacherID) REFERENCES users(userID),
  PRIMARY KEY (teamID)
);

CREATE TABLE rubric (
  rubricID INT NOT NULL AUTO_INCREMENT,
  rubricName VARCHAR(50),
  rubricDate VARCHAR(50),
  teacherID INT,
  FOREIGN KEY (teacherID) REFERENCES users(userID),
  PRIMARY KEY (rubricID)
);

CREATE TABLE question (
  questionID INT NOT NULL AUTO_INCREMENT,
  questionDesc VARCHAR(250),
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

CREATE TABLE rubricAssignment (
  rubricAssignmentID INT NOT NULL AUTO_INCREMENT,
  rubricID INT,
  teamID INT,
  FOREIGN KEY (rubricID) REFERENCES team(teamID),
  PRIMARY KEY (rubricAssignmentID)
);

CREATE TABLE questionAssignment (
  questionAssignmentID INT NOT NULL AUTO_INCREMENT,
  rubricID INT,
  questionID INT,
  FOREIGN KEY (rubricID) REFERENCES rubric(rubricID),
  FOREIGN KEY (questionID) REFERENCES question(questionID),
  PRIMARY KEY (questionAssignmentID)
);