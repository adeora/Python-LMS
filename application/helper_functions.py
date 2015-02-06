## PACKAGE IMPORTS

from application import app #bleh. circular imports. needed though...
import sqlite3 #for database stuff
from flask import g, session, escape #flask g object...needed
from functools import wraps

DATABASE = 'database.db' # database location

#make a db connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

#close connection on app teardown
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

#query the database
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

#insert a value into the db
def insert_db(query, args=()):
	""" USED LIKE SO:
			insert_db('insert into entries (title, text) values (?, ?)',[request.form['title'], request.form['text']])
	"""
	db = get_db()
	db.execute(query, args)
	db.commit()


##############
### STUDENT FUNCS
#######


def validate_student(func):
	"""
		Validates students. If not logged in, redirects to login.
		If a student, redirects to student page. Otherwise, nothing.
		I have no idea how most of this works, so don't touch anything.
		To use, put '@validate_teacher' after app route definition.
	"""
	@wraps(func)
	def f(*args, **kwds):
		if not 'isTeacher' in session:
			return redirect("/")
		if session['isTeacher'] == 1:
			return redirect("/teachers/")
		return func(*args, **kwds)
	return f

def getStudentClasses():
	classData = query_db("SELECT classes.id, classes.name FROM classes JOIN roster ON roster.class_id = classes.id where people_id=?;", [session['id']])
	classes = []
	for classThing in classData:
		holder = {}
		holder['id'] = classThing[0]
		holder['name'] = classThing[1]
		classes.append(holder)
	return classes


def getStudentGrades(class_id):
	"""
		Gets all the grades given to the logged-in student.
	"""
	grades = []
	quizGrades = query_db("SELECT quizzes.name, grade FROM quiz_grades JOIN quizzes ON quiz_grades.quiz_id=quizzes.id JOIN topics on quizzes.topic_id=topics.id JOIN classes ON topics.class_id=classes.id WHERE student_id=? AND topics.class_id=?;", [session['id'], class_id])
	for grade in quizGrades:
		holderDict = {}
		holderDict['thing_name'] = grade[0]
		holderDict['grade'] = grade[1]
		grades.append(holderDict)
	assignmentGrades = query_db("SELECT assignments.name, grade FROM assignment_grades JOIN assignments ON assignment_grades.assignment_id=assignments.id JOIN topics on assignments.topic_id=topics.id JOIN classes ON topics.class_id=classes.id WHERE student_id=? AND topics.class_id=?;", [session['id'], class_id])
	for grade in assignmentGrades:
		holderDict = {}
		holderDict['thing_name'] = grade[0]
		holderDict['grade'] = grade[1]
		grades.append(holderDict)
	return grades


#################
###TEACHER FUNCS
##################


def validate_teacher(func):
	"""
		Validates teachers. If not logged in, redirects to login.
		If a student, redirects to student page. Otherwise, nothing.
		I have no idea how most of this works, so don't touch anything.
		To use, put '@validate_teacher' after app route definition.
	"""
	@wraps(func)
	def f(*args, **kwds):
		if not 'isTeacher' in session:
			return redirect("/")
		if session['isTeacher'] == 0:
			return redirect("/students/")
		return func(*args, **kwds)
	return f


def getTeacherClasses():
	"""
		Gets the classes that a teacher teaches.
	"""
	classData = query_db("select id, name from classes where teacher_id = ?;", [session['id']])
	classes = []
	for part in classData:
		holderDict = {}
		holderDict['id'] = part[0]
		holderDict['name'] = str(part[1])
		classes.append(holderDict)
	return classes

def getAllTeacherTopics():
	"""
		Gets the topics that a teacher has.
	"""
	topicData = query_db("select topics.id, topics.name, classes.name from topics join classes on topics.class_id=classes.id where teacher_id=?;", [session['id']])
	topics = []
	for topic in topicData:
		holderDict = {}
		holderDict['id'] = topic[0]
		holderDict['name'] = escape(str(topic[1]))
		holderDict['class'] = escape(str(topic[2]))
		topics.append(holderDict)
	return topics

def getClassTopics(class_id):
	"""
		Gets all of the topics in a class.
	"""
	topicData = query_db("select id, name from topics where class_id=?", [class_id])
	topics = []
	for topic in topicData:
		holderDict = {}
		holderDict['id'] = topic[0]
		holderDict['name'] = topic[1]
		topics.append(holderDict)
	return topics

def getTeacherAssignments():
	"""
		Gets all of the assignments for a teacher.
	"""
	assignmentData = query_db("select assignments.id, assignments.name, assignments.due_date from assignments join topics on assignments.topic_id=topics.id join classes on topics.class_id=classes.id where teacher_id=?;", [session['id']])
	assignments = []
	for assignment in assignmentData:
		holderDict = {}
		holderDict['id'] = assignment[0]
		holderDict['name'] = assignment[1]
		holderDict['due_date'] = assignment[2]
		assignments.append(holderDict)
	return assignments

def getClassAssignments(class_id):
	"""
		Gets all of the assignments for a class.
	"""
	assignmentData = query_db("select id, name, due_date from assignments where topic_id=(select id from topics where class_id=?);", [class_id])
	assignments = []
	for assignment in assignmentData:
		holderDict = {}
		holderDict['id'] = assignment[0]
		holderDict['name'] = str(assignment[1])
		holderDict['due_date'] = assignment[2]
		assignments.append(holderDict)
	return assignments

def getTopicAssignments(topic_id):
	"""
		Gets all of the assignments for a topic.
	"""
	assignmentData = query_db("select id, name, due_date from assignments where topic_id=?;", [topic_id])
	assignments = []
	for assignment in assignmentData:
		holderDict = {}
		holderDict['id'] = assignment[0]
		holderDict['name'] = str(assignment[1])
		holderDict['due_date'] = assignment[2]
		assignments.append(holderDict)
	return assignments

def getTeacherQuizzes():
	"""
		Gets all of the quizzes created by the logged-in teacher.
	"""
	quizData = query_db("select id, name from quizzes where creator_id=?;", [session['id']])
	quizzes = []
	for quiz in quizData:
		holderDict = {}
		holderDict['id'] = quiz[0]
		holderDict['name'] = quiz[1]
		quizzes.append(holderDict)
	return quizzes

def getTopicQuizzes(topic_id):
	"""
		Gets all of the quizzes in a particular topic.
	"""
	quizData = query_db("select id, name from quizzes where topic_id=?;", [topic_id])
	quizzes = []
	for quiz in quizData:
		holderDict = {}
		holderDict['id'] = quiz[0]
		holderDict['name'] = quiz[1]
		quizzes.append(holderDict)
	return quizzes

def getClassQuizzes(class_id):
	"""
		Gets all of the quizzes in a particular class.
	"""
	quizData = query_db("SELECT quizzes.id, quizzes.name FROM quizzes JOIN topics ON topics.id=quizzes.topic_id WHERE topics.class_id=?;", [class_id])
	quizzes = []
	for quiz in quizData:
		holderDict = {}
		holderDict['id'] = quiz[0]
		holderDict['name'] = quiz[1]
		quizzes.append(holderDict)
	return quizzes

def getRegisteredStudents(class_id):
	"""
		Gets all of the students registered for a class.
	"""
	studentData = query_db("SELECT people.id, name FROM people JOIN roster ON roster.people_id=people.id WHERE roster.class_id=?;", [class_id])
	people = []
	for person in studentData:
		holderDict = {}
		holderDict['id'] = person[0]
		holderDict['name'] = person[1]
		people.append(holderDict)
	return people

def getClassGrades(class_id):
	"""
		Gets all of the grades given to a class.
	"""
	
	grades = []
	quizGrades = query_db("SELECT people.name, quizzes.name, grade FROM quiz_grades JOIN people ON quiz_grades.student_id=people.id JOIN quizzes ON quiz_grades.quiz_id=quizzes.id JOIN topics ON quizzes.topic_id=topics.id JOIN classes ON topics.class_id=classes.id WHERE classes.id=?;", [class_id])
	for grade in quizGrades:
		holderDict = {}
		holderDict['student_name'] = grade[0]
		holderDict['thing_name'] = str(grade[1]) + " (Quiz)"
		holderDict['grade'] = grade[2]
		grades.append(holderDict)
	assignmentGrades = query_db("SELECT people.name, assignments.name, grade FROM assignment_grades JOIN people ON assignment_grades.student_id=people.id JOIN assignments ON assignment_grades.assignment_id=assignments.id JOIN topics ON assignments.topic_id=topics.id JOIN classes ON topics.class_id=classes.id WHERE classes.id=?;", [class_id])
	for grade in assignmentGrades:
		holderDict = {}
		holderDict['student_name'] = grade[0]
		holderDict['thing_name'] = str(grade[1]) + " (Assignment)"
		holderDict['grade'] = grade[2]
		grades.append(holderDict)
	return grades
