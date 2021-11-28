from flask import (Flask, render_template, request,Response, redirect, session, make_response)
from flask import render_template
import mysql.connector
import sys
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import json
import time
import random

global current_error
current_error = []

global indexDir
indexDir = "/"
global loginDir
loginDir = "/login"
global userDir
userDir = "/user"
global userDashboardDir
userDashboardDir = "/user_dashboard"
global adminDashboardDir
adminDashboardDir = "/admin_dashboard"
global logoutDir
logoutDir = "/logout"
global errorDir
errorDir = "/error"
global createUserDir
createUserDir = "/create_user"
global settingsDir
settingsDir = "/settings"
global counter
counter = 1


localHost = False

def readUserFromDatabase(user):
    global current_error
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E")
        cursor = mydb.cursor(buffered=True)
        cursor.execute("SELECT User,Password FROM User WHERE User='%s'" % (user))
        row = cursor.fetchone()
        cursor.close()
        if row is not None:
            return row
        return None
    except Exception as e:
        current_error.append(str(e))
        return None


def writeUserToDatabase(user, password):
    global current_error
    try:
        if user == "" or password == "":
            return False
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E")
        cursor = mydb.cursor(buffered=True)
        sql = "INSERT INTO User(User,Password) VALUES(%s,%s)"
        val = (user, password)
        cursor.execute(sql, val)
        mydb.commit()
        cursor.close()
    except Exception as e:
        current_error.append(str(e))
        return False
    return True

def alterUserInDatabase(newUser,oldUser,newPassword):
    global current_error
    try:
        if newUser == "" or oldUser == "":
            return False
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E")
        cursor = mydb.cursor(buffered=True)
        current_error.append(newUser)
        sql = "UPDATE M7011E.User SET User='{}', Password='{}' WHERE User='{}'".format(newUser,newPassword,oldUser)
        val = (newUser,oldUser)
        cursor.execute(sql)
        mydb.commit()
        cursor.close()
    except Exception as e:
        current_error.append(str(e))
        return False
    return True


class User:
    def __init__(self, username, password=None):
        if password == None:
            try:
                self.name = username["user"]
                self.password = username["password"]
                self.validated = username["valid"]
            except:
                self.name = ""
                self.password = ""
                self.validated = False
            return
        self.name = username
        self.password = password
        self.validated = False

    def isValid(self):
        return self.validated

    def validate(self):
        if self.validated:
            session["user"] = self.toJSON()
            return True
        user = readUserFromDatabase(self.name)
        if user and check_password_hash(user[1], self.password):
            self.validated = True
            session["user"] = self.toJSON()
            return True
        else:
            return False

    def toJSON(self):
        return {"user": self.name, "password": self.password, "valid": self.validated}


def fetchKey():
    global current_error
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E")
        cursor = mydb.cursor(buffered=True)
        cursor.execute("SELECT Secret FROM SessionSecret WHERE ServerName='Flask'")
        cursor.close()
        return str(cursor.fetchone())
    except Exception as e:
        current_error.append(str(e))
        return "supersecretpassword"


def getUser():
    try:
        if "user" in session:
            return User(session["user"])
    except Exception as e:
        current_error.append(str(e))
        return None


def checkSession():
    user = getUser()
    if user != None and user.isValid():
        return user
    else:
        return None


host = "0.0.0.0"
app = Flask(__name__)
app.secret_key = fetchKey()
app.permanent_session_lifetime = timedelta(minutes=10)


@app.route(errorDir)
def error():
    global current_error
    return "<p>" + str(current_error) + "</p>"


@app.route(indexDir)
def index():
    if checkSession():
        return redirect(userDashboardDir)
    return render_template("index.html")


@app.route(loginDir, methods=['POST', 'GET'])
def login():
    if checkSession():
        return redirect(userDashboardDir)

    global current_error
    if request.method == 'POST':
        try:
            username = request.form.get("username")
            password = request.form.get("password")
            currentUser = User(username, password)
            if currentUser.validate():
                # login successful
                return redirect(userDashboardDir)
            else:
                return render_template("login.html", error="Invalid username or password")
        except Exception as e:
            current_error.append(str(e))
            return redirect(errorDir)
    else:
        return render_template("login.html")


@app.route("/data")
def data():
    mydb = mysql.connector.connect(
        host="localhost",
        user="Client",
        password="")
    cursor = mydb.cursor(buffered=True)
    cursor.execute("SELECT * FROM M7011E.User")
    s = "<h>Stuff in the database</h><br><p>"
    for x in cursor:
        s = s + str(x)
    cursor.close()
    return s + "</p>"


@app.route(createUserDir, methods=['POST', 'GET'])
def signup():
    if checkSession():
        return redirect(userDashboardDir)
    err = ""
    if request.method == 'POST':
        user = User(request.form.get("username"), request.form.get("password"))

        if user.password != request.form.get("password-repeat"):
            err = "Passwords don't match"
        elif writeUserToDatabase(user.name, generate_password_hash(user.password)):
            if user.validate():
                return redirect(userDashboardDir)  ## Successful signup!!
            else:
                err = "Server error: Created but could not validate new user :("
        else:
            err = "Existing user or server SNAFU :("

    return render_template("create_user.html", error=err)


@app.route(userDashboardDir)
def userDash():
    if (localHost):
        return render_template("user_dashboard.html")
    else:
        user = checkSession()
        if user:
            return render_template("user_dashboard.html",user=user.name)
        else:
            return redirect(indexDir)

@app.route(adminDashboardDir)
def adminDash():
    if (localHost):
        return render_template("admin_dashboard.html")
    else:
        user = checkSession()
        if user:
            return render_template("admin_dashboard.html",user=user.name)
        else:
            return redirect(indexDir)



@app.route(logoutDir)
def logout():
    global current_error
    try:
        session.pop("user")
    except Exception as e:
        current_error.append(str(e))
    return redirect(indexDir)

@app.route(settingsDir,methods=['POST', 'GET'])
def settings():
    user = checkSession()
    if user:
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            flag = False
            if username and username != "":
                #user.name = username
                if alterUserInDatabase(username,user.name):
                    user.name = username
                    flag = True
                    #user.validate()
            if password and password != "":
                user.password = password

                    #return redirect(dashboardDir)
                #else:
                #    return render_template("settings.html",user=user.name)
        else:
            return render_template("settings.html",user=user.name)
    else:
        return redirect(indexDir)

@app.route("/fetch",methods=['POST', 'GET'])
def fetch():
    if checkSession() == None:
        redirect(indexDir)
    if request.method == 'POST':
        global counter
        data = {
            "time": counter,
            "value":random.randint(0,100)
        }
        counter = counter+1
        return json.dumps(data)
    else:
        return "BAD REQUEST"

if __name__ == "__main__":
    if(localHost):
        app.run(host)
    else:
        app.run(host, ssl_context='adhoc')
