import mysql.connector


def fetchKey():
    """! Fetches the secret key from the database.
    @return A secret key to use for Flask session encryption
    """
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
        return "supersecretpassword"

def readUserFromDatabase(user):
    """! Fetches data surrounding a singular user from the database.
    @param user Client user name
    @return User information of None
    """
    global current_error
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E")
        cursor = mydb.cursor(buffered=True)
        cursor.execute("SELECT User,Password,Postalcode,Root FROM User WHERE User='%s'" % (user))
        row = cursor.fetchone()
        cursor.close()
        if row is not None:
            return row
        return None
    except Exception as e:
        return None

def readAllUserFromDatabase():
    """! Fetches data surrounding all users from the database.
    @return Info for all users ro None.
    """
    global current_error
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E")
        cursor = mydb.cursor(buffered=True)
        cursor.execute("SELECT User,Password,Postalcode,LastOnline,Root,LoginIP,LoginPort FROM User")
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        return None

def fetchUserImage(username):
    """! Fetches a user's chosen image from the database.
    @param username Client user name.
    @return User image or None
    """
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
        return None

def setUserImage(username, blob):
    """! Inserts a user's chosen image to the database.
    @param username Client user name.
    @param blob Photo blob.
    @return True if the image was set. False otherwise.
    """
    global current_error
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E",
            autocommit=False)
        cursor = mydb.cursor(buffered=True)
        cursor.execute(
            "UPDATE M7011E.User SET Image=%s WHERE User='%s'" % (blob, username))
        mydb.commit()
        cursor.close()
        return True
    except Exception as e:
        return False

def writeUserToDatabase(user, password, postalcode):
    """! Adds a user to the database.
    @param user User name.
    @param password Hashed password.
    @return True if the user was written to the database. False otherwise.
    """
    global current_error
    try:
        if user == "" or password == "":
            return False
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E",
            autocommit=False)
        cursor = mydb.cursor(buffered=True)
        sql = "INSERT INTO User(User,Password,Postalcode) VALUES(%s,%s,%s)"
        val = (user, password, postalcode)
        cursor.execute(sql, val)
        mydb.commit()
        cursor.close()
    except Exception as e:
        return False
    return True

def alterUserInDatabase(username, newPassword=None, newPostalCode=None):
    """! Alters information surrounding a user in the database.
    @param username Client user name.
    @param newPassword New password for the user.
    @param newPostalCode New postal code for the user.
    @return True if the user was updated in the database. False otherwise.
    """
    global current_error
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E",
            autocommit=False)
        cursor = mydb.cursor(buffered=True)
        sql = "UPDATE M7011E.User SET "
        if newPassword:
            sql += "Password='%s'" % (newPassword)
        if newPostalCode:
            sql += "Postalcode='%s'" % (newPostalCode)
        sql += "WHERE User='%s'" % (username)
        cursor.execute(sql)
        mydb.commit()
        cursor.close()
    except Exception as e:
        current_error.append(str(e))
        return False
    return True

def removeUserFromDatabase(username):
    """! Deletes a user from the database.
    @param username Client user name
    @return True if the user was deleted from the database. False otherwise.
    """
    global current_error
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E",
            autocommit=False)
        cursor = mydb.cursor(buffered=True)
        cursor.execute("DELETE FROM M7011E.User WHERE User='%s'" % (username))
        mydb.commit()
        cursor.close()
        return True
    except Exception as e:
        return False


def updateUserLastLogin(username, date, ip="255.255.255.255", port="1234"):
    """! Update the user login date, IP number and port on the database. Call this whenever a uer logs in or updates their login info.
    @param username Client user name.
    @param date Current cate.
    @param ip Login IP.
    @param port Login port.
    @return True if the user login was updated. False otherwise.
    """
    global current_error
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E",
            autocommit=False)
        cursor = mydb.cursor(buffered=True)
        sql = "UPDATE M7011E.User SET LastOnline='{}', LoginIP='{}',LoginPort='{}' WHERE User='{}'".format(date, ip,
                                                                                                           port,
                                                                                                           username)
        cursor.execute(sql)
        mydb.commit()
        cursor.close()
    except Exception as e:
        return False
    return True

def setHistoricalData(username, data):
    """! Add historical data to a selected user.
    @param username Client user name.
    @data JSON data object as a string.
    @return True if the historical data was set. False otherwise.
    """
    global current_error
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E",
            autocommit=False)
        cursor = mydb.cursor(buffered=True)
        sql = "UPDATE M7011E.User SET HistoricalData='{}' WHERE User='{}'".format(data, username)
        cursor.execute(sql)
        mydb.commit()
        cursor.close()
    except Exception as e:
        return False
    return True

def getHistoricalData(user):
    """! Retrieve historical data from a selected user.
    @param Client user name.
    @return Historical data as it is stored in the database or None
    """
    global current_error
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E")
        cursor = mydb.cursor(buffered=True)
        cursor.execute("SELECT HistoricalData FROM User WHERE User='%s'" % (user))
        row = cursor.fetchone()
        cursor.close()
        if row is not None:
            return row
        return None
    except Exception as e:
        return None
