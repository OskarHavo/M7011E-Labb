from flask import Flask
from flask import render_template
import mysql.connector

host="0.0.0.0"
app = Flask(__name__)

@app.route("/powerplants")
def index():
        return render_template("index.html")

@app.route("/login")
def login():
	return render_template("login.html")
@app.route("/data")
def data():
	mydb = mysql.connector.connect(
	host = "localhost",
    	user = "Client",
    	password = "")
	cursor = mydb.cursor()
	cursor.execute("SELECT * FROM M7011E.Demo")
	s = "<h>Stuff in the database</h><br><p>"
	for x in cursor:
		s = s + str(x)
	return s+"</p>"

if __name__ == "__main__":
	app.run(host)
