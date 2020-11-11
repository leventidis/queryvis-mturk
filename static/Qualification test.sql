DROP DATABASE IF EXISTS QualificationTest;
CREATE DATABASE QualificationTest;
USE QualificationTest;

/* Problem 1 */
DROP TABLE IF EXISTS Students;
CREATE TABLE Students(
	StudentID INT PRIMARY KEY AUTO_INCREMENT,
	Student_Name VARCHAR(50)
);

DROP TABLE IF EXISTS Courses;
CREATE TABLE Courses(
	CourseID INT PRIMARY KEY AUTO_INCREMENT,
	Course_Name VARCHAR(50)
);

DROP TABLE IF EXISTS StudentCourseRegistration;
CREATE TABLE StudentCourseRegistration(
	RegistrationID INT PRIMARY KEY AUTO_INCREMENT,
	StudentID INT,
    CourseID INT,
	CONSTRAINT Registeration_fk_Students FOREIGN KEY (StudentID)
        REFERENCES Students (StudentID)
        ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT Registeration_fk_Courses FOREIGN KEY (CourseID)
        REFERENCES Courses (CourseID)
        ON UPDATE CASCADE ON DELETE CASCADE
);
INSERT INTO Students(Student_Name) VALUES('Student No1');
INSERT INTO Students(Student_Name) VALUES('Student No2');
INSERT INTO Students(Student_Name) VALUES('Student A');
INSERT INTO Students(Student_Name) VALUES('Student B');
INSERT INTO Students(Student_Name) VALUES('Student C');
INSERT INTO Students(Student_Name) VALUES('Student AB');
INSERT INTO Students(Student_Name) VALUES('Student ABC');


INSERT INTO Courses(Course_Name) VALUES('Course A');
INSERT INTO Courses(Course_Name) VALUES('Course B');
INSERT INTO Courses(Course_Name) VALUES('Course C');

INSERT INTO StudentCourseRegistration(StudentID, CourseID) VALUES(
	(SELECT StudentID FROM Students WHERE Student_Name = 'Student A' LIMIT 1),
    (SELECT CourseID FROM Courses WHERE Course_Name = 'Course A' LIMIT 1));
INSERT INTO StudentCourseRegistration(StudentID, CourseID) VALUES(
	(SELECT StudentID FROM Students WHERE Student_Name = 'Student B' LIMIT 1),
    (SELECT CourseID FROM Courses WHERE Course_Name = 'Course B' LIMIT 1));
INSERT INTO StudentCourseRegistration(StudentID, CourseID) VALUES(
	(SELECT StudentID FROM Students WHERE Student_Name = 'Student C' LIMIT 1),
    (SELECT CourseID FROM Courses WHERE Course_Name = 'Course C' LIMIT 1));
INSERT INTO StudentCourseRegistration(StudentID, CourseID) VALUES(
	(SELECT StudentID FROM Students WHERE Student_Name = 'Student AB' LIMIT 1),
    (SELECT CourseID FROM Courses WHERE Course_Name = 'Course A' LIMIT 1));
INSERT INTO StudentCourseRegistration(StudentID, CourseID) VALUES(
	(SELECT StudentID FROM Students WHERE Student_Name = 'Student AB' LIMIT 1),
    (SELECT CourseID FROM Courses WHERE Course_Name = 'Course B' LIMIT 1));   
INSERT INTO StudentCourseRegistration(StudentID, CourseID) VALUES(
	(SELECT StudentID FROM Students WHERE Student_Name = 'Student ABC' LIMIT 1),
    (SELECT CourseID FROM Courses WHERE Course_Name = 'Course A' LIMIT 1));
INSERT INTO StudentCourseRegistration(StudentID, CourseID) VALUES(
	(SELECT StudentID FROM Students WHERE Student_Name = 'Student ABC' LIMIT 1),
    (SELECT CourseID FROM Courses WHERE Course_Name = 'Course B' LIMIT 1)); 
INSERT INTO StudentCourseRegistration(StudentID, CourseID) VALUES(
	(SELECT StudentID FROM Students WHERE Student_Name = 'Student ABC' LIMIT 1),
    (SELECT CourseID FROM Courses WHERE Course_Name = 'Course C' LIMIT 1)); 
/* Show names of courses that 'Student A' Registered for  */
/* A */
SELECT c.Course_Name
	FROM Courses c 
		INNER JOIN StudentCourseRegistration r ON c.CourseID = r.CourseID
		INNER JOIN Students s ON s.StudentID = r.StudentID
	WHERE Student_Name = 'Student A';
/* Alternative version */
SELECT c.Course_Name
	FROM Courses c, StudentCourseRegistration r, Students s 
	WHERE Student_Name = 'Student A'
	and c.CourseID = r.CourseID
	and s.StudentID = r.StudentID;



/* Problem 2 */    
/* Show courses with course names and the number of student in each course */
SELECT Course_Name, COUNT(*) FROM Courses c JOIN StudentCourseRegistration r ON c.CourseID = r.CourseID GROUP BY r.CourseID;
SELECT Course_Name, COUNT(*) FROM Courses c NATURAL JOIN StudentCourseRegistration r GROUP BY r.CourseID;

/* Problem 3 */
/* Find students who registered for some course or courses. */
SELECT * FROM Students WHERE StudentID = ANY(Select StudentID FROM StudentCourseRegistration); 
/* Problem 4 */
DROP TABLE IF EXISTS Forums;
CREATE TABLE Forums(
	ForumID INT PRIMARY KEY AUTO_INCREMENT,
	Forum_Name VARCHAR(50)
);
CREATE TABLE Posts(
	PostID INT PRIMARY KEY AUTO_INCREMENT,
	Post_ForumID INT,
    Post_Author VARCHAR(50),
    Post_DateTime DATETIME,
    Post_Content LONGTEXT,
	CONSTRAINT Posts_fk_Forums FOREIGN KEY (Post_ForumID)
        REFERENCES Forums (ForumID)
        ON UPDATE CASCADE ON DELETE CASCADE    
);
INSERT INTO Forums(Forum_Name) VALUES ('Sports');
INSERT INTO Forums(Forum_Name) VALUES ('Politics');
INSERT INTO Forums(Forum_Name) VALUES ('Economics');

INSERT INTO Posts(Post_ForumID, Post_Author, Post_DateTime, Post_Content) VALUES(
	(SELECT ForumID FROM Forums WHERE Forum_Name = 'Sports' LIMIT 1),
    'Author A', '2015-01-05 01:05', "Post Content A");
INSERT INTO Posts(Post_ForumID, Post_Author, Post_DateTime, Post_Content) VALUES(
	(SELECT ForumID FROM Forums WHERE Forum_Name = 'Sports' LIMIT 1),
    'Author B', '2016-01-06 01:06', "Post Content B");
INSERT INTO Posts(Post_ForumID, Post_Author, Post_DateTime, Post_Content) VALUES(
	(SELECT ForumID FROM Forums WHERE Forum_Name = 'Sports' LIMIT 1),
    'Author C', '2017-01-07', "Post Content C");
INSERT INTO Posts(Post_ForumID, Post_Author, Post_DateTime, Post_Content) VALUES(
	(SELECT ForumID FROM Forums WHERE Forum_Name = 'Economics' LIMIT 1),
    'Author D', '2018-01-08 01:08', "Post Content D");
INSERT INTO Posts(Post_ForumID, Post_Author, Post_DateTime, Post_Content) VALUES(
	(SELECT ForumID FROM Forums WHERE Forum_Name = 'Economics' LIMIT 1),
    'Author E', '2019-01-09 01:09', "Post Content E");

/* List posts that were posted after January 1, 2017 0:0:0*/
SELECT * FROM Posts WHERE Post_DateTime > '2017-01-01 0:0:0';
/* Problem 5 */

/* Suppose the following schema: 
Forums (ForumID, Forum_Name) 
Posts (ForumID, PostID, Post_Titile, Post_Author, Post_Content, Post_DateTime)
*/
/* List forums that have no post */
SELECT * FROM Forums WHERE NOT EXISTS (SELECT * FROM Posts WHERE Post_ForumID = ForumID);

SELECT * FROM Forums WHERE (SELECT * FROM Posts WHERE Post_ForumID = ForumID) = 0;
/* Problem 6 */
/* List all forums with thier name in which there are at least 2 posts*/
SELECT Forum_Name, COUNT(PostID) FROM Posts JOIN Forums ON ForumID = Post_ForumID GROUP BY Post_ForumID HAVING COUNT(PostID) >= 2;
