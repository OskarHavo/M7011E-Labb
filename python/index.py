import binascii
import json

from flask import (Flask, render_template, request, Response, redirect, session, make_response, jsonify)

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime

from flask_socketio import SocketIO

import databaseFunctions
from dynamic_table import *
from databaseFunctions import *

from simulator import *

from windmillhistory import Windmillhistory

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
global createUserDir
createUserDir = "/create_user"
global settingsDir
settingsDir = "/settings"
global tableDir
tableDir = "/table"
global counter
counter = 1

host = "0.0.0.0"
app = Flask(__name__)
app.secret_key = databaseFunctions.fetchKey()
app.permanent_session_lifetime = timedelta(minutes=999)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 megabytes
socketio = SocketIO(app)

global manager
manager = SimulationManager(10, socketio)
dataHistory = Windmillhistory(manager)


class User:
    def __init__(self, username, password=None, postalcode=97753, root=False):
        if password == None:
            try:
                self.name = username["user"]
                self.password = username["password"]
                self.validated = username["valid"]
                self.postalcode = username["postalcode"]
                self.root = username["root"]
                self.ip = request.environ['REMOTE_ADDR']
                self.port = request.environ['REMOTE_PORT']
            except:
                self.name = username
                self.password = ""
                self.postalcode = ""
                self.validated = False
                self.root = False
                self.ip = request.environ['REMOTE_ADDR']
                self.port = request.environ['REMOTE_PORT']
            return
        self.name = username
        self.password = password
        self.postalcode = postalcode
        self.root = False
        self.validated = False
        self.ip = request.environ['REMOTE_ADDR']
        self.port = request.environ['REMOTE_PORT']

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
            self.root = user[3] == 1
            session["user"] = self.toJSON()
            return True
        else:
            return False

    def toJSON(self):
        return {"user": self.name, "password": self.password, "valid": self.validated, "postalcode": self.postalcode,
                "root": self.root, "ip": self.ip, "root": self.root}


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
        updateUserLastLogin(user.name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user.ip, user.port)
        return user
    else:
        return None


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

    if request.method == 'POST':
        try:
            username = request.form.get("username")
            password = request.form.get("password")
            currentUser = User(username, password)
            if currentUser.validate():
                # login successful
                if currentUser.root:
                    return redirect(adminDashboardDir)
                else:
                    return redirect(userDashboardDir)
            else:
                return render_template("login.html", error="Invalid username or password")
        except:
            return render_template("login.html", error="Server Error")
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
        user = User(request.form.get("username"), request.form.get("password"),
                    allowedPostalcode(request.form.get("postalcode")))
        if not user.postalcode:
            err = "Invalid postalcode\n"
        if user.password != request.form.get("password-repeat"):
            err = err + "Passwords don't match\n"
        elif writeUserToDatabase(user.name, generate_password_hash(user.password), user.postalcode):
            if user.validate():
                return redirect(userDashboardDir)  ## Successful signup!!
            else:
                err = err + "Server error: Created but could not validate new user :("
        else:
            err = err + "Existing user or server SNAFU :("

    return render_template("create_user.html", error=err)


@app.route(userDashboardDir)
def userDash():
    user = checkSession()
    if user:
        if user.root:
            return redirect(adminDashboardDir)
        return render_template("user_dashboard.html", user=user.name, postalcode=user.postalcode)
    else:
        return redirect(indexDir)


@app.route("/user_dashboard/<username>")
def userDash2(username):
    user = checkSession()

    if user and user.root:
        userdata = readUserFromDatabase(username)
        if userdata:
            session["user-backup"] = user.toJSON()
            user = User(userdata[0], userdata[1])
            user.validated = True
            user.postalcode = userdata[2]
            session["user"] = user.toJSON()
            return render_template("user_dashboard.html", user=user.name)
        return redirect(adminDash)
    else:
        return redirect(indexDir)


@app.route(adminDashboardDir)
def adminDash():
    user = checkSession()
    if user and user.root:
        return render_template("admin_dashboard.html", user=user.name)
    else:
        return redirect(indexDir)


@app.route(logoutDir)
def logout():
    global current_error
    try:
        if "user-backup" in session:
            session["user"] = session["user-backup"]
            session.pop("user-backup")
            return redirect(adminDashboardDir)
        else:
            session.pop("user")
    except Exception as e:
        current_error.append(str(e))
    return redirect(indexDir)


@app.route(settingsDir, methods=['POST', 'GET'])
def settings():
    user = checkSession()
    if user:
        if request.method == "POST":

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
                return render_template("settings.html", user=user.name, error=error)

            if alterUserInDatabase(user.name, password, postalcode):
                if postalcode:
                    user.postalcode = postalcode
                if password:
                    user.password = password
                session["user"] = user.toJSON()
                return redirect(userDashboardDir)

            return render_template("settings.html", user=user.name)
        else:
            return render_template("settings.html", user=user.name)
    else:
        return redirect(indexDir)


@app.route(settingsDir + "/delete", methods=["POST"])
def delete_user():
    user = checkSession()
    if user and request.method == "POST":
        if removeUserFromDatabase(user.name):
            manager.stopNode(user.name)
            return redirect(logoutDir)
        else:
            render_template("settings.html", user=user.name, error="Could not delete user")
    else:
        return redirect(indexDir)


@app.route("/image/<usertype>", methods=["POST", "GET"])
def image(usertype):
    user = checkSession()
    if user:
        if request.method == "POST":
            if 'houseimage' not in request.files:
                return ""
            file = request.files["houseimage"]

            file = file.read()

            bin_file = "0x" + binascii.hexlify(file).decode("utf-8")

            if setUserImage(user.name, bin_file):
                print("uploaded image")
            else:
                print("could not upload image")

            if usertype == "admin":
                return redirect("/admin_dashboard")
            else:
                return redirect("/user_dashboard")
        else:
            data = fetchUserImage(user.name)
            if data:
                response = make_response(data[0])
                response.headers.set('Content-Type', 'image/jpg')
                response.headers.set('Content-Disposition', 'attachment', filename='house.jpg')
                return response


# TODO User verification
@app.route("/fetch", methods=['POST', 'GET', 'PUT'])
def fetch():
    user = checkSession()
    if request.method == "POST":
        if not user:
            return "{}"

        function = request.values.json["function"]
        if function == "create":
            if user.name != "" and user.postalcode != "":
                manager.startNode(user.name, int(user.postalcode), [0, 2], [0, 2])
        elif function == "delete":
            if user:
                manager.stopNode(user.name)
        return jsonify({"data": request.args.get("username")})
    elif request.method == "GET":
        if user:
            data = getHistoricalData(user.name)
            if data:
                return jsonify(json.loads(data[0].decode("utf-8")))
            else:
                return "{}"
        else:
            print("Invalid user!!!")
            return "{}"
    elif request.method == "PUT":
        if user:
            valueName = request.json["valueName"]
            data = request.json["data"]
            manager.alterNode(user.name, valueName, data)
            return "{}"
    return "{}"


@app.route("/block_user/<username>")
def block_user(username):
    user = checkSession()
    if user and user.root:
        manager.alterNode(username, "block", "")
        return redirect(adminDashboardDir)
    else:
        return redirect(indexDir)


@app.route("/fetch_admin", methods=['GET', 'PUT'])
def fetch_admin():
    user = checkSession()
    if not user or not user.root:
        return "{}"
    if request.method == "GET":
        return jsonify(manager.powerplant.getCurrentData())
    elif request.method == "PUT":
        valueName = request.json["valueName"]
        data = request.json["data"]
        manager.powerplant.setValue(valueName, data)
        return "{}"
    else:
        return "{}"


@app.route("/fetch_all_users_for_admin", methods=['GET'])
def fetch_all_users():
    if True:
        user = checkSession()
        if user and user.root:
            users = readAllUserFromDatabase()

            if users:
                items = []
                delta = timedelta(minutes=10)
                now = datetime.now()
                for user in users:
                    if user[4] == 1:
                        continue

                    user_status = "Online"
                    if user[3] < now - delta:
                        user_status = "Offline"
                    if manager.getNode(user[0]).getBlockStatus():
                        user_status = "Blocked"
                    if "rubbe hitta bra condition" == True:
                        user_status = "Blackout"

                    items.append(Row(
                        user[0],
                        user_status,
                        "window.location.href='/user_dashboard/%s';" % user[0],
                        "window.location.href='/block_user/%s';" % user[0],
                        user[5],
                        user[6])
                    )
                table = UserTable(items)
                return jsonify({"table": str(table.__html__())})
    return "{}"


def stream_callback(data, timestamp, sessiondata, sid):
    sessiondata["timestamp"] = str(timestamp)
    socketio.emit("stream partition", (data, sessiondata), callback=stream_data, to=sid)


""" This function can only be called if the client has received a callback from the server.
    The client must first ask the server to start a streaming session. """


def stream_data(sessionData):
    timestamp = datetime.strptime(sessionData["timestamp"], "%Y-%m-%d %H:%M:%S")

    if sessionData["user"]:

        sessionData["valid"] = False
        windmill = manager.getNode(sessionData["user"])
        data, nextTimestamp = windmill.getNext(timestamp, stream_callback, sessionData, sessionData["sid"])

        if data:
            sessionData["timestamp"] = str(nextTimestamp)
            print("Streaming data for user ", sessionData["user"], "at timestamp", nextTimestamp, " and length",
                  len(data))
            # Send the newly fetched data to the client.
            socketio.emit("stream partition", (data, sessionData), callback=stream_data, to=sessionData["sid"])
    else:
        print("Some user tried to be sneaky and stream data!")


# Start a data streaming session
@socketio.on("start stream")
def start_stream():
    user = checkSession()
    if user:
        manager.startNode(user.name, int(user.postalcode), [0, 2], [0, 2])
        startTime = datetime.now()
        print("Starting stream for user", user.name)
        sessionData = user.toJSON()

        sessionData["valid"] = False
        sessionData["sid"] = request.sid
        sessionData["timestamp"] = str(str(startTime - timedelta(seconds=100, microseconds=startTime.microsecond)))
        stream_data(sessionData)  ## timedelta lets us fetch previous windmill updates


@socketio.on('connect')
def socket_connect():
    user = checkSession()
    if user:
        print("client", user.name, "with sid", request.sid, "connected :)")


@socketio.on('disconnect')
def socket_disconnect():
    user = checkSession()
    if user:
        print("client", user.name, "with sid", request.sid, "disconnected :(")


def serverStartup():
    try:
        users = readAllUserFromDatabase()

        for user in users:
            if user[4] == 0:
                manager.startNode(user[0], int(user[2]), [0, 2], [0, 2])
    except:
        print("Running without database! Are you connected?")
    dataHistory.start(socketio)
    socketio.run(app, host=host)


if __name__ == "__main__":
    serverStartup()
