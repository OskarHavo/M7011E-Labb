import mysql.connector


""""Fetches the secret key from the database"""
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
        return "supersecretpassword"

""""Fetches data surrounding a singular user from the database"""
def readUserFromDatabase(user):
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

""""Fetches data surrounding all users from the database"""
def readAllUserFromDatabase():
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

""""Fetches a user's chosen image from the database"""
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
        return None

""""Inserts a user's chosen image to the database"""
def setUserImage(username, blob):
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
        return False

""""Adds a user to the database"""
def writeUserToDatabase(user, password, postalcode):
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
        val = (user, password, postalcode)
        cursor.execute(sql, val)
        mydb.commit()
        cursor.close()
    except Exception as e:
        return False
    return True

""""Alters information surrounding a user in the database"""
def alterUserInDatabase(username, newPassword=None, newPostalCode=None):
    global current_error
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E")
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

""""Deletes a user from the database"""
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
        return False


"""Update the user login date, IP number and port on the database. Call this whenever a uer logs in or updates their login info"""
def updateUserLastLogin(username, date, ip="255.255.255.255", port="1234"):
    global current_error
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E")
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

""""Add historical data to a selected user"""
def setHistoricalData(username, data):
    global current_error
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="Client",
            password="",
            database="M7011E")
        cursor = mydb.cursor(buffered=True)
        sql = "UPDATE M7011E.User SET HistoricalData='{}' WHERE User='{}'".format(data, username)
        cursor.execute(sql)
        mydb.commit()
        cursor.close()
    except Exception as e:
        return False
    return True

""""Retrieve historical data from a selected user"""
def getHistoricalData(user):
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
