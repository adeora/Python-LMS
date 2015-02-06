from application import app
from flask import render_template, session, redirect, request, flash, escape
from functools import wraps
from helper_functions import *

@app.route('/students/')
@validate_student
def student_home():
	return render_template('/students/index.html', classes=getStudentClasses())

@app.route('/students/classes/')
@validate_student
def student_classes_home():
	return render_template('/students/classes.html', classes=getStudentClasses())

@app.route('/students/classes/join/', methods=['POST'])
@validate_student
def student_class_join():
	insert_db("INSERT INTO roster (people_id, class_id) VALUES (?, ?);", [session['id'], request.form['id']])
	flash("You joined the class with an id of %s" %(request.form['id']))
	return redirect("/students/classes")

@app.route('/students/class/<class_id>/')
@validate_student
def student_class_page(class_id):
	className = query_db("SELECT name FROM classes WHERE id=?;", [class_id], one=True)
	return render_template('/students/class_page.html', class_name=str(className[0]), topics=getClassTopics(class_id), assignments=getClassAssignments(class_id), quizzes=getClassQuizzes(class_id), grades=getStudentGrades(class_id))

@app.route('/students/topics/<topic_id>/')
@validate_student
def student_topic_page(topic_id):
	topicName = query_db("SELECT name FROM topics WHERE id=?;", [topic_id], one=True)
	return render_template('/students/topic_page.html', topic_name=str(topicName[0]), assignments=getTopicAssignments(topic_id), quizzes=getTopicQuizzes(topic_id))

@app.route('/students/quizzes/<quiz_id>/')
@validate_student
def student_quiz_page(quiz_id):
	quizName = query_db("SELECT name FROM quizzes WHERE id=?;", [quiz_id])
	result = query_db("SELECT grade from quiz_grades WHERE quiz_id=? AND student_id=?;", [quiz_id, session['id']], one=True) #check if the person has already taken the test
	if result == None:
		questionData = query_db("SELECT id, question_text, a_answer_text, b_answer_text, c_answer_text, d_answer_text FROM questions WHERE quiz_id=?;", [quiz_id])
		questions = []
		for question in questionData:
			holderDict = {}
			holderDict['id'] = question[0]
			holderDict['text'] = question[1]
			holderDict['answers'] = [str(question[2]), str(question[3]), str(question[4]), str(question[5])]
			questions.append(holderDict)
		return render_template('/students/quiz_page.html', questions = questions,quiz_name=quizName[0][0], quiz_id=quiz_id)
	else:
		flash("You receieved a grade of {0}% on this quiz.".format(result[0]))
		return render_template('/students/quiz_page.html', quiz_name=quizName[0][0])

@app.route('/students/quizzes/grade/<quiz_id>/', methods=['POST'])
@validate_student
def grade_quiz(quiz_id):
	correct = 0.0
	questions = 0.0
	data = request.form
	question_ids  = [int(i) for i in data]
	answers = []
	for i in data: ##creates a list of the answers submitted 
		answers.append(eval("int(data['%s'])"%(i))) #ohmygod eww
	
	for i in range(len(answers)):
		correctAnswer = query_db("SELECT correct_answer FROM questions WHERE id=?;", [question_ids[i]], one=True)
		if int(correctAnswer[0]) == answers[i]:
			correct += 1.0
		questions += 1.0
	percent = (correct/questions)*100
	insert_db("INSERT INTO quiz_grades (student_id, quiz_id, grade) VALUES (?, ?, ?);", [session['id'], quiz_id, percent])
	return redirect("/students/quizzes/%s/"%(quiz_id))

@app.route('/students/assignments/<assignment_id>/')
@validate_student
def student_assignment_page(assignment_id):
	assignmentData = query_db("SELECT name, description, due_date FROM assignments WHERE id=?;", [assignment_id], one=True)
	name = assignmentData[0]
	description = assignmentData[1]
	due_date = assignmentData[2]
	return render_template('/students/assignment_page.html', name=name, description=description, due_date=due_date)
