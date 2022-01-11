from windmill import Windmill
import threading
from energyCentral import EnergyCentral

class NodeManager:
    """! Our nodemanager class. This acts as a container for windmills and takes care of starting and stopping them.
    """
    def __init__(self, delta, ID, *var):
        """! Init
        @param delta Update delta given in seconds.
        @param var  Windmill init variables. See Windmill for more info.
        """
        self.client = Windmill(ID, *var)
        self.delta = delta
        self.mutex = threading.Lock()
        self.running = False

    def stop(self):
        """! Stops the node. """
        with self.mutex:
            self.running = False

    def run(self, socketio):
        """! Starts the node.
        @param socketio A reference to the global socketIO object.
        """
        with self.mutex:
            self.running = True
        while True:
            with self.mutex:
                if not self.running:
                    break
            data = self.client.tick()
            socketio.sleep(self.delta)

class SimulationManager:
    """! Our simulation manager class, responsible for the windmill simulations.
    """
    def __init__(self, globalDelta, socketio, availableEnergy=100):
        """! Init.
        @param globalDelta The energy central update delta given in seconds.
        @param socketio Reference to the global socketIO object.
        @param availableEnergy Maximum available energy to give to all clients. Default = 100.
        """
        self.productionNodes = {}  # Username, thread
        self.delta = globalDelta
        self.mutex = threading.Lock()
        self.powerplant = EnergyCentral(availableEnergy, self.delta)
        socketio.start_background_task(EnergyCentral.run, self.powerplant, socketio)
        self.socketio = socketio

    def __del__(self):
        """! Stops the energy central and all active windmills. """
        with self.mutex:
            for key in self.productionNodes:
                self.productionNodes[key].stop()
        self.powerplant.stop()

    def startNode(self, ID, *var):
        """! This starts a windmill simulation for a user if one has not been started yet.
        @param ID Client user name
        @param var Windmill init parameters
        """
        with self.mutex:
            if not ID in self.productionNodes:
                self.productionNodes[ID] = NodeManager(self.delta, ID, *var, self.powerplant)
                self.socketio.start_background_task(NodeManager.run, self.productionNodes[ID], self.socketio)

    def alterNode(self, username, valueName, data):
        """! Alters the windmill.
        @param username Client username.
        @param valueName Name of the value to change.
        @param data Value to set
        """
        with self.mutex:
            self.productionNodes[username].client.setValue(valueName, data)

    def stopNode(self, ID):
        """! Stops the windmill.
        @param ID Client user name
        """
        with self.mutex:
            if ID in self.productionNodes:
                self.productionNodes[ID].stop()

    def getNode(self, ID):
        """! Returns a windmill based on a client username.
        @param ID Client user name
        """
        with self.mutex:
            if ID in self.productionNodes:
                return self.productionNodes[ID].client
