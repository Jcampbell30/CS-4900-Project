CREATE DATABASE peerReviewDatabase;

CREATE TABLE user (
  userID INT NOT NULL AUTO_INCREMENT,
  userFirstName VARCHAR(50),
  userLastName VARCHAR(50),
  email VARCHAR(100),
  password VARCHAR(50),
  role VARCHAR(50),
  PRIMARY KEY (userID)
);

CREATE TABLE team (
  teamID INT NOT NULL AUTO_INCREMENT,
  teamName VARCHAR(50),
  userID INT,
  FOREIGN KEY (userID) REFERENCES user(userID),
  PRIMARY KEY (teamID)
);

CREATE TABLE rubric (
  rubricID INT NOT NULL AUTO_INCREMENT,
  path VARCHAR(255)
  PRIMARY KEY (rubricID)
);

CREATE TABLE teamAssignment (
  teamAssignmentID INT NOT NULL AUTO_INCREMENT,
  teamID INT,
  userID INT,
  FOREIGN KEY (teamID) REFERENCES team(teamID),
  FOREIGN KEY (userID) REFERENCES user(userID),
  PRIMARY KEY (teamAssignmentID)
);

CREATE TABLE rubricAssignment (
  rubricAssignmentID INT NOT NULL AUTO_INCREMENT,
  rubricID INT,
  teamID INT,
  FOREIGN KEY (rubricID) REFERENCES team(teamID),
  FOREIGN KEY (userID) REFERENCES user(userID)
  PRIMARY KEY (rubricAssignmentID)
);