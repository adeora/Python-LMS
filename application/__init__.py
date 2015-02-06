from flask import Flask, url_for, request, render_template
app = Flask(__name__)

import application.helper_functions
import application.index
import application.students
import application.teachers
import application.login
