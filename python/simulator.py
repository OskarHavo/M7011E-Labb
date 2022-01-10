import windmill
import threading
import requests
from EnergyCentral import EnergyCentral

"""Class describing the database and its functions"""
class Database:
    """Init"""
    def __init__(self):
        self.database = {}
        self.lock = threading.Lock()

    """Append new data"""
    def put(self, data, username):
        with self.lock:
            if len(self.database[username]) >= 10:
                self.database[username] = self.database[username][1:]
            self.database[username].append(data)

    """Add new user"""
    def new(self, username):
        self.database[username] = []

    """Remove user"""
    def remove(self, username):
        with self.lock:
            if username in self.database:
                del self.database[username]

    """Get user"""
    def get(self, username):
        with self.lock:
            if username in self.database:
                return self.database[username]
            else:
                return None

"""Get but formatted correctly"""
def formatGet(data):
    result = "?"
    for key in data:
        result = result + str(key) + "=" + data[key] + "&"
    return result[:-1]

"""Our Restful API message bus class"""
class MessageBus:
    """Init"""
    def __init__(self, server_url):
        self.server = server_url
        self.mutex = threading.Lock()
        return

    """PUT request"""
    def PUT(self, data):
        with self.mutex:
            response = requests.put(self.server, data=data)
            if response.status_code == 200:
                return response.json()
            else:
                return None

    """POST request"""
    def POST(self, data):
        with self.mutex:
            response = requests.post(self.server, data=data)
            if response.status_code == 200:
                return response.json()
            else:
                return None

    """GET request"""
    def GET(self, subdir):
        with self.mutex:
            response = requests.get(self.server + subdir)
            return response.json()

"""Our nodemanager class"""
class NodeManager:
    """Init"""
    def __init__(self, messageBus, delta, ID, var, powerplant):
        self.client = windmill.ProductionNode(ID, var[0], var[1], var[2], powerplant)
        self.delta = delta
        self.mutex = threading.Lock()
        self.running = False
        self.messageBus = messageBus

    """Stops the node"""
    def stop(self):
        with self.mutex:
            self.running = False

    """Starts the node"""
    def run(self, socketio):
        with self.mutex:
            self.running = True
        while True:
            with self.mutex:
                if not self.running:
                    break
            data = self.client.tick()
            socketio.sleep(self.delta)

"""Our simulation manager class, responible for the windmill simulations"""
class SimulationManager:
    """Init"""
    def __init__(self, globalDelta, socketio, availableEnergy=100):
        self.productionNodes = {}  # Username, thread
        self.delta = globalDelta
        self.bus = MessageBus("http://localhost:4242")
        self.mutex = threading.Lock()
        self.powerplant = EnergyCentral(availableEnergy, self.delta)
        socketio.start_background_task(EnergyCentral.run, self.powerplant, socketio)
        self.socketio = socketio

    """Stops the windmill"""
    def __del__(self, instance):
        self.powerplant.stop()

    """This starts a windmill simulation for a user if one has not been started yet."""
    def startNode(self, ID, *var):
        with self.mutex:
            if not ID in self.productionNodes:
                self.productionNodes[ID] = NodeManager(self.bus, self.delta, ID, var, self.powerplant)
                self.socketio.start_background_task(NodeManager.run, self.productionNodes[ID], self.socketio)

    """Alters the windmill"""
    def alterNode(self, username, valueName, data):
        with self.mutex:
            self.productionNodes[username].client.setValue(valueName, data)

    """Stops the windmill"""
    def stopNode(self, ID):
        with self.mutex:
            if ID in self.productionNodes:
                self.productionNodes[ID].stop()

    """Returns the windmill?"""
    def getNode(self, ID):
        with self.mutex:
            if ID in self.productionNodes:
                return self.productionNodes[ID].client

    """Deletes ? """
    def __del__(self):
        with self.mutex:
            for key in self.productionNodes:
                self.productionNodes[key].stop()
