from application import app
from flask import request, render_template, session, redirect

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/logout/")
def logout():
	session.pop('id', None)
	session.pop('isTeacher', None)
	return redirect("/")
