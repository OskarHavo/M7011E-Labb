import windmill
from time import sleep
import threading
import requests
from EnergyCentral import EnergyCentral
#from flask import Flask, jsonify, request
#global app



class Database:
    def __init__(self):
        self.database = {}
        self.lock = threading.Lock()

    def put(self,data,username):
        with self.lock:
            if len(self.database[username]) >= 10:
                self.database[username] = self.database[username][1:]
            self.database[username].append(data)
    def new(self,username):
        self.database[username] = []
    def remove(self,username):
        with self.lock:
            if username in self.database:
                del self.database[username]
    def get(self,username):
        with self.lock:
            if username in self.database:
                return self.database[username]
            else:
                return None



def formatGet(data):
    result = "?"
    for key in data:
        result = result + str(key) + "=" + data[key] + "&"
    return result[:-1]

class MessageBus:
    def __init__(self,server_url):
        self.server=server_url
        self.mutex = threading.Lock()
        return
    def PUT(self,data):
        with self.mutex:
            response = requests.put(self.server,data=data)
            if response.status_code == 200:
                return response.json()
            else:
                return None
    def POST(self,data):
        with self.mutex:
            response = requests.post(self.server,data=data)
            if response.status_code == 200:
                return response.json()
            else:
                return None
    def GET(self,subdir):
        with self.mutex:
            response = requests.get(self.server + subdir)
            return response.json()

class NodeManager:
    def __init__(self,messageBus, delta,ID,var,powerplant,database):
        self.client = windmill.ProductionNode(ID,var[0],var[1],var[2],powerplant)
        self.delta = delta
        self.mutex = threading.Lock()
        self.running = False
        self.messageBus = messageBus
        self.database = database
    def stop(self):
        with self.mutex:
            self.running = False

    def run(self):
        with self.mutex:
            self.running = True
        while True:
            with self.mutex:
                if not self.running:
                    break
            data = self.client.tick()
            self.database.put(data,self.client.user)
            sleep(self.delta)



class SimulationManager:
    def __init__(self,globalDelta,database,availableEnergy = 100):
        self.productionNodes = {}   # Username, thread
        self.delta = globalDelta
        self.bus = MessageBus("http://localhost:4242")
        self.mutex = threading.Lock()
        self.powerplant = EnergyCentral(availableEnergy,self.delta)
        thread = threading.Thread(target=EnergyCentral.run,args=(self.powerplant,))
        thread.start()
        self.database = database

    def __del__(self, instance):
        self.powerplant.stop()

    ## This starts a windmill simulation for a user if one has not been started yet.
    def startNode(self,ID,*var):
        with self.mutex:
            if not ID in self.productionNodes:
                self.productionNodes[ID] = NodeManager(self.bus,self.delta,ID,var,self.powerplant,self.database)
                thread = threading.Thread(target=NodeManager.run,args=(self.productionNodes[ID],))
                thread.start()
    def alterNode(self,username,valueName,data):
        with self.mutex:
            self.productionNodes[username].client.setValue(valueName,data)
            #del self.productionNodes[oldID]
    def stopNode(self,ID):
        with self.mutex:
            if ID in self.productionNodes:
                self.productionNodes[ID].stop()
    def getNode(self,ID):
        with self.mutex:
            if ID in self.productionNodes:
                return self.productionNodes[ID].client
    def __del__(self):
        with self.mutex:
            for key in self.productionNodes:
                self.productionNodes[key].stop()

#host = "0.0.0.0"
#app = Flask(__name__)

"""
def run():
    app.run(port=4242)

#global manager
#manager = SimulationManager(4)

if __name__ == "__main__":


    thread = threading.Thread(target=run)
    thread.start()
    sleep(1)
    print("hello")

    manager.bus.POST({"username":"robyn","postalCode":97753,"function":"create"})
    #manager.alterNode("robyn","sellRatio","1")
    #manager.bus.POST({"username":"Oskar","postalCode":97755})

    i = 0
    while True:
        print(manager.bus.GET(formatGet({"username":"robyn"})))
        sleep(4)
        i = i +1
        if i == 10:
            break;


    print("Stopping")
    del manager
    sleep(1)
    print("Stopped all")
    #thread.join()
"""