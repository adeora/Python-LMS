"""
	TSA Learning Management System v1.2
	Author: Abhimanyu Deora
	Description: A Learning Management System created with Flask for the 2013 TSA National Competition.
	License: CC Attribution-NonCommercial-ShareAlike 4.0 International
"""

#imports everything from the application folder
from application import app

app.secret_key = '$JLmL!eCQXyajbdu2LCJ&Vwqs2JGagg3B&FRfexCmKBV'

#starts the server, debug mode is on
app.debug = True
app.run()
