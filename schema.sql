CREATE TABLE user (
  userid INT PRIMARY KEY,
  userFirstName VARCHAR(50),
  userLastName VARCHAR(50),
  email VARCHAR(100),
  password VARCHAR(50),
  role VARCHAR(50)
);

CREATE TABLE team (
  teamId INT PRIMARY KEY,
  teamName VARCHAR(50),
  userid INT,
  FOREIGN KEY (userid) REFERENCES user(userid)
);

CREATE TABLE rubric (
  rubricID INT PRIMARY KEY,
  path VARCHAR(255)
);

CREATE TABLE teamAssignment (
  teamID INT,
  userID INT,
  PRIMARY KEY (teamID, userID),
  FOREIGN KEY (teamID) REFERENCES team(teamID),
  FOREIGN KEY (userID) REFERENCES user(userID)
);
