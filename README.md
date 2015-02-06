# TSA Learning Management System- Version 1.2 #

## Description ##

This is a Learning Management System created for the 2014 TSA National Conference, and built with Flask.

To keep the code nice and modular, the app is organized as such:


* / - The database and the main Python file. The run.py file imports all of the main application logic from the application folder.
	- application/ - Various files with all of the views and helper functions.
		* static/ - Static files loaded by the views.
		* templates/ - All of the templates used for the views
			- teachers/ - Views for the teachers
			- students/ - Views for the students

