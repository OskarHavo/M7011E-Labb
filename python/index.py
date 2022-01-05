import binascii
import sys

from flask import (Flask, render_template, request, Response, redirect, session, make_response, jsonify)
from flask import render_template
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime
from io import StringIO
from flask_socketio import SocketIO

import simulator
from simulator import *

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
global tableDir
tableDir = "/table"
global counter
counter = 1

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

host = "0.0.0.0"
app = Flask(__name__)
app.secret_key = fetchKey()
app.permanent_session_lifetime = timedelta(minutes=999)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 # 2 megabytes
socketio = SocketIO(app)

global temporaryDatabase
temporaryDatabase = Database()

global manager
manager = SimulationManager(10,temporaryDatabase)

def readUserFromDatabase(user):
    global current_error
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E")
        cursor = mydb.cursor(buffered=True)
        cursor.execute("SELECT User,Password,Postalcode FROM User WHERE User='%s'" % (user))
        row = cursor.fetchone()
        cursor.close()
        if row is not None:
            return row
        return None
    except Exception as e:
        current_error.append(str(e))
        return None

def fetchUserImage(username):
    global current_error
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E")
        cursor = mydb.cursor(buffered=True)
        cursor.execute(
            "SELECT Image FROM User WHERE User='%s'" % (username))
        row = cursor.fetchone()
        cursor.close()
        if row is not None:
            return row
        return None
    except Exception as e:
        current_error.append(str(e))

def setUserImage(username,blob):
    global current_error
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E")
        cursor = mydb.cursor(buffered=True)
        cursor.execute(
            "UPDATE M7011E.User SET Image=%s WHERE User='%s'" % (blob, username))
        mydb.commit()
        cursor.close()
        return True
    except Exception as e:
        current_error.append(str(e))
        return False


def writeUserToDatabase(user, password,postalcode):
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
        sql = "INSERT INTO User(User,Password,Postalcode) VALUES(%s,%s,%s)"
        val = (user, password,postalcode)
        cursor.execute(sql, val)
        mydb.commit()
        cursor.close()
    except Exception as e:
        current_error.append(str(e))
        return False
    return True

def alterUserInDatabase(username,newPassword=None,newPostalCode=None):
    global current_error
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E")
        cursor = mydb.cursor(buffered=True)
        sql = "UPDATE M7011E.User SET "# Password='{}' WHERE User='{}'".format(newUser,newPassword,oldUser)
        if newPassword:
            sql += "Password='%s'" %(newPassword)
        if newPostalCode:
            sql += "Postalcode='%s'" %(newPostalCode)
        sql += "WHERE User='%s'" % (username)
        print(sql)
        cursor.execute(sql)
        mydb.commit()
        cursor.close()
    except Exception as e:
        current_error.append(str(e))
        return False
    return True

def removeUserFromDatabase(username):
    global current_error
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E")
        cursor = mydb.cursor(buffered=True)
        cursor.execute("DELETE FROM M7011E.User WHERE User='%s'" % (username))
        mydb.commit()
        cursor.close()
        return True
    except Exception as e:
        current_error.append(str(e))
        return False

def updateUserLastLogin(username,date):
    global current_error
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E")
        cursor = mydb.cursor(buffered=True)
        sql = "UPDATE M7011E.User SET LastOnline='{}' WHERE User='{}'".format(date,username)
        cursor.execute(sql)
        mydb.commit()
        cursor.close()
    except Exception as e:
        current_error.append(str(e))
        return False
    return True


class User:
    def __init__(self, username,password=None,postalcode=97753):
        if password == None:
            try:
                self.name = username["user"]
                self.password = username["password"]
                self.validated = username["valid"]
                self.postalcode = username["postalcode"]
            except:
                self.name = username
                self.password = ""
                self.postalcode = ""
                self.validated = False
            return
        self.name = username
        self.password = password
        self.postalcode = postalcode

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
            self.postalcode = user[2]
            session["user"] = self.toJSON()
            return True
        else:
            return False

    def toJSON(self):
        return {"user": self.name, "password": self.password, "valid": self.validated,"postalcode":self.postalcode}

## Check if the postal code is valid or not
def allowedPostalcode(code):
    code = code.replace(" ", "")
    if code and code != "":
        try:
            int(code)
        except:
            return None
        return code
    return None

def allowedPassword(password):
    if password and len(password) > 3:
        return password
    return None

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
        updateUserLastLogin(user.name,datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return user
    else:
        return None

@app.route(errorDir)
def error():
    global current_error
    return "<p>" + str(current_error) + "</p>"


@app.route(indexDir)
def index():
    if checkSession():
        return redirect(userDashboardDir)
    return render_template("index.html")


@app.route(tableDir)
def table():
    return "I am table."


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
        user = User(request.form.get("username"),request.form.get("password"),allowedPostalcode(request.form.get("postalcode")))
        if not user.postalcode:
            err = "Invalid postalcode\n"
        if user.password != request.form.get("password-repeat"):
            err = err+ "Passwords don't match\n"
        elif writeUserToDatabase(user.name, generate_password_hash(user.password),user.postalcode):
            if user.validate():
                return redirect(userDashboardDir)  ## Successful signup!!
            else:
                err = err+"Server error: Created but could not validate new user :("
        else:
            err = err+"Existing user or server SNAFU :("

    return render_template("create_user.html", error=err)


@app.route(userDashboardDir)
def userDash():
    user = checkSession()
    ##if user:
    return render_template("user_dashboard.html",user=user.name,postalcode=user.postalcode)
    ##else:
    ##    return redirect(indexDir)

@app.route("/user_dashboard/<username>")
def userDash2(username):
    user = User(username,"")
    user.postalcode = "97753"
    user.validated = True
    session["user"] = user.toJSON()
    if user:
        return render_template("user_dashboard.html",user=user.name)
    else:
        return redirect(indexDir)

@app.route(adminDashboardDir)
def adminDash():
    user = checkSession()
    if user:
        return render_template("admin_dashboard.html",user=user.name)
    else:
        return redirect(indexDir)

@app.route("/admin_dashboard/<username>")
def adminDash2(username):
    user = User(username, "")
    user.postalcode = "97753"
    user.validated = True
    session["user"] = user.toJSON()
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
            #username = request.form.get("username")
            password = request.form.get("password")
            postalcode = request.form.get("postalcode")


            error = ""
            if postalcode:
                postalcode = allowedPostalcode(postalcode)
                if not postalcode:
                    error += "No valid postal code\n"
            if password:
                password = allowedPassword(password)
                if not password:
                    error += "No valid password"
            if error != "":
                return render_template("settings.html",user=user.name,error=error)

            if alterUserInDatabase(user.name,password,postalcode):
                if postalcode:
                    user.postalcode = postalcode
                if password:
                    user.password = password
                session["user"] = user.toJSON()
                return redirect(userDashboardDir)

            return render_template("settings.html", user=user.name)
        else:
            return render_template("settings.html",user=user.name)
    else:
        return redirect(indexDir)

@app.route(settingsDir+"/delete",methods=["POST"])
def delete_user():
    user = checkSession()
    if user and request.method == "POST":
        if removeUserFromDatabase(user.name):
            return redirect(logoutDir)
        else:
            render_template("settings.html",user=user.name,error="Could not delete user")
    else:
        return redirect(indexDir)


@app.route("/image",methods=["POST","GET"])
def image():
    user = checkSession()
    if user:
        if request.method == "POST":
            if 'houseimage' not in request.files:
                return ""

#            bin_file = io.BytesIO(request.files["houseimage"].read()).getvalue()
            file = request.files["houseimage"]

            file = file.read()

            bin_file = "0x" + binascii.hexlify(file).decode("utf-8")

            if setUserImage(user.name,bin_file):
                print("uploaded image")
            else:
                print("could not upload image")
            return redirect("/user_dashboard")
        else:
            data = fetchUserImage(user.name)
            if data:
                response = make_response(data[0])
                response.headers.set('Content-Type','image/jpg')
                response.headers.set('Content-Disposition','attachment',filename='house.jpg')
                return response

# TODO User verification
@app.route("/fetch",methods = ['POST', 'GET','PUT'])
def fetch():
    user = checkSession()
    if request.method == "POST":
        if not user:
            return "{}"
        #postalCode = request.values.json["postalCode"]
        function = request.values.json["function"]
        if function == "create":
            if user.name != "" and user.postalcode != "":
                temporaryDatabase.new(user.name)
                manager.startNode(user.name,int(user.postalcode),[-5,5],[-5,5])
        elif function == "delete":
            if user:
                temporaryDatabase.remove(user.name)
        return jsonify({"data":request.args.get("username")})
    elif request.method == "GET":
        if user:
            data = fetchUserImage(user.name)
            if data:
                return jsonify({"image":data[0]})
            #if not temporaryDatabase.get(user.name):
            #    temporaryDatabase.new(user.name)
            #    manager.startNode(user.name, int(user.postalcode), [-1, 1], [-1, 1])
            #return jsonify(temporaryDatabase.get(user.name)[-1])
        else:
            print("Invalid user!!!")
            return "{}"
    elif request.method == "PUT":
        if user:
        #username = request.values.get("username")
            valueName = request.json["valueName"]
            data = request.json["data"]
            manager.alterNode(user.name,valueName,data)
            return "{}"
    return "{}"

@app.route("/fetch_admin",methods = ['GET','PUT'])
def fetch_admin():
    if request.method == "GET":
        user = checkSession()   ## TODO set to admin user instead
        if user:
            return jsonify(manager.powerplant.getCurrentData())
    elif request.method == "PUT":
        user = checkSession()   ## TODO set to admin user instead
        #username = request.values.get("username")
        valueName = request.json["valueName"]
        data = request.json["data"]
        manager.powerplant.setValue(valueName,data)
        return "{}"
    else:
        return "{}"

def stream_data():
    user = checkSession()
    if user:
        if not temporaryDatabase.get(user.name):
            temporaryDatabase.new(user.name)
            manager.startNode(user.name, int(user.postalcode), [-1, 1], [-1, 1])
        socketio.emit("stream partition", temporaryDatabase.get(user.name)[-1], callback=stream_data)
    else:
        print("User",user.name,"tried to be sneaky and stream data!")


@socketio.on("start stream")
def start_stream(data):
    stream_data()

@socketio.on('connect')
def socket_connect():
    user = checkSession()
    if user:
        print("client", user.name, "connected :)")
        #socketio.emit("server response",callback=ack)


@socketio.on('disconnect')
def socket_disconnect():
    user = checkSession()
    if user:
        print("client",user.name,"disconnected :(")


if __name__ == "__main__":
    socketio.run(app,host=host)#, ssl_context='adhoc')
