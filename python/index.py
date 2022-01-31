import binascii
import json
import databaseFunctions

from flask import (Flask, render_template, request, Response, redirect, session, make_response, jsonify)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime
from flask_socketio import SocketIO
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
    """! The structure of a user."""
    def __init__(self, username, password=None, postalcode=97753, root=False):
        """! Init.
        @param username User name.
        @param password User password in clear text.
        @param postalcode User postal code.
        @param root Admin status for the user.
        """
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
        """! Check if the user is validated by the server.
        @return True if the user has been validated.
        """
        return self.validated
    def validate(self):
        """! Validate the user in the database from the server, to prevent fraudulent users.
        @return True if the user is valid.
        """
        if self.validated:
            session["user"] = self.toJSON()
            return True
        user = readUserFromDatabase(self.name)
        if user and check_password_hash(user[1], self.password):
            self.validated = True
            self.postalcode = user[2]
            self.root = user[3] == 1    # This is where we grant root status to a user.
            session["user"] = self.toJSON()
            return True
        else:
            return False
    def toJSON(self):
        """! Output as JSON.
        @return The user in a JSON format.
        """
        return {"user": self.name, "password": self.password, "valid": self.validated, "postalcode": self.postalcode,
                "root": self.root, "ip": self.ip, "root": self.root}


def allowedPostalcode(code):
    """! Check if the postal code is valid or not.
    @return An integer representation of the postal code or None
    """
    code = code.replace(" ", "")
    if code and code != "":
        try:
            int(code)
        except:
            return None
        return code
    return None

def allowedPassword(password):
    """! Check if the password is valid or not. All passwords must be of length 4 or more. There is a max
    value in the database, but I forgot what I set it to.
    @return The password or None
    """
    if password and len(password) > 3:
        return password
    return None

def getUser():
    """! Get the user from a session.
    @return A user object or None
    """
    try:
        if "user" in session:
            return User(session["user"])
    except Exception as e:
        current_error.append(str(e))
        return None

def checkSession():
    """! Check if the user is valid or not.
    @return A user object or None.
    """
    user = getUser()
    if user != None and user.isValid():
        if "user-backup" not in session:
            updateUserLastLogin(user.name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user.ip, user.port)
        return user
    else:
        return None

@app.route(indexDir)
def index():
    """"! Flask function for showing the index.
    @return The index page
    """
    if checkSession():
        return redirect(userDashboardDir)
    return render_template("index.html")

@app.route(loginDir, methods=['POST','GET'])
def login():
    """! Flask function for log in page.
    @return On valid POST: the admin or user home page\n Otherwise: The login page.
    """
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


@app.route(createUserDir, methods=['POST','GET'])
def signup():
    """! Flask function for signing up a user.
    @return On valid POST: Redirect to the user home page\n Otherwise: Return to signup with an error.
    """
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
    """! Flask function for showing the user dashboard.
    @return For valid user: The user home page. \n Otherwise: Redirect to index directory.
    """
    user = checkSession()
    if user:
        if user.root:
            return redirect(adminDashboardDir)
        return render_template("user_dashboard.html", user=user.name, postalcode=user.postalcode)
    else:
        return redirect(indexDir)

@app.route("/user_dashboard/<username>")
def userDash2(username):
    """! Flask function for switching to a user's dashboard from a root user.
    @param username The user name you want to access.
    @return For valid root user and other user: The user home page. \n Otherwise: Redirect to index page.
    """
    user = checkSession()

    if user and user.root:
        userdata = readUserFromDatabase(username)
        if userdata and userdata[3] == 0:
            session["user-backup"] = user.toJSON()
            user = User(userdata[0], userdata[1])
            user.validated = True
            user.postalcode = userdata[2]
            session["user"] = user.toJSON()
            return redirect(userDashboardDir)
        return redirect(adminDash)
    else:
        return redirect(indexDir)

@app.route(adminDashboardDir)
def adminDash():
    """! Flask function for showing the admin dashboard.
    @return For valid root user: The admin home page.
    """
    user = checkSession()
    if user and user.root:
        return render_template("admin_dashboard.html", user=user.name)
    else:
        return redirect(indexDir)

@app.route(logoutDir)
def logout():
    """! Flask function for logging out.
    @return For Root user logged in as another user: Return to root home page. \n Otherwise: The index page.
    """
    if "user-backup" in session:
        session["user"] = session["user-backup"]
        session.pop("user-backup")
        return redirect(adminDashboardDir)
    elif "user" in session:
        session.pop("user")

    return redirect(indexDir)

@app.route(settingsDir, methods=['POST','GET'])
def settings():
    """! Flask function for changing your settings.
    @return On valid POST: Change user settings. \n Otherwise: Return to index page.
    """
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
    """! Flask function for deleting users.
    @return On valid POST: Delete the user and redirect to logout page.
    """
    user = checkSession()
    if user and request.method == "POST":
        if removeUserFromDatabase(user.name):
            manager.stopNode(user.name)
            return redirect(logoutDir)
        else:
            render_template("settings.html", user=user.name, error="Could not delete user")
    else:
        return redirect(logoutDir)

@app.route("/image/<usertype>", methods=["POST", "GET"])
def image(usertype):
    """! Flask adding/getting images.
    @return On valid POST: Set the user image.\n On valid GET: Fetch the user image if there is one.
    """
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
            else:
                return ""





@app.route("/fetch", methods=['POST', 'GET', 'PUT'])
def fetch():
    """! This is our old version for fetching windmill information. As you can see, there is no streaming going on here.
    """
    user = checkSession()
    """
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
        """
    if request.method == "GET":
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
    """! Flask function for blocking users.
    @return Redirect to the index page if current user is not root. Otherwise go to root home page.
    """
    user = checkSession()
    if user and user.root:
        manager.alterNode(username, "block", "")
        return redirect(adminDashboardDir)
    else:
        return redirect(indexDir)

@app.route("/fetch_admin", methods=['GET', 'PUT'])
def fetch_admin():
    """!
    This function fetches information from the EnergyCentral object and returns it to the user. We have not
    stream-ified data from the energy central, but we could if we wanted to.

    The PUT function is used to change the energy central state.

    @return On valid GET: Current Energy central state and output. \n On valid PUT: Nothing
    """
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
    """!
    @return On valid GET: A JSON structure containing all regular users in the database.
    """
    if True:
        user = checkSession()
        if user and user.root:
            users = readAllUserFromDatabase()

            if users:
                items = []
                delta = timedelta(seconds=30)   # Very quick update time for logged in/out
                # We only store the last login time and date. Online/offline info is determined by the delta.

                now = datetime.now()
                for user in users:
                    if user[4] == 1:
                        continue

                    user_status = "Online"
                    if user[3] < now - delta:
                        user_status = "Offline"
                    if manager.getNode(user[0]).getBlockStatus():
                        user_status = "Blocked"
                    if manager.powerplant.clients[user[0]]["powerOutage"]:
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
    """!
    This function is used as callback for when a windmill has no information to send. The windmill will
    call this functions which sends the newly generated data to the client.
    """
    sessiondata["timestamp"] = str(timestamp)
    socketio.emit("stream partition", (data, sessiondata), callback=stream_data, to=sid)



def stream_data(sessionData):
    """! This function is used to stream data from the server to the clients.
    The client must first ask the server to start a streaming session.

    Warning: Due to some SocketIO and Flask shenanigans, this function is not running inside the safety of flask,
    so we don't have any encrypted cookies etc. If this text is still here, it means that I haven't fixed the
    issue or added our own method of encrypting the session data.
    This could potentially be used as a backdoor to data streaming.

    @param sessionData User session data.
    """


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


@socketio.on("start stream")
def start_stream():
    """! "Start a data streaming session."""
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
    """! Socket connection feedback function. This just prints some info to the console."""
    user = checkSession()
    if user:
        print("client", user.name, "with sid", request.sid, "connected :)")

@socketio.on('disconnect')
def socket_disconnect():
    """! Socket disconnect feedback function. This just prints some info to the console. """
    user = checkSession()
    if user:
        print("client", user.name, "with sid", request.sid, "disconnected :(")

def serverStartup():
    """! Start the server. """
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
