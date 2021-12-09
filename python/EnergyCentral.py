import threading
from time import sleep
import dataGeneration
class EnergyCentral:
    def __init__(self, maxCapacity,delta):
        self.currentCapacity = maxCapacity
        self.maxCapacity = maxCapacity
        self.currentConsumption = 0
        self.clients = []
        self.running = True
        self.sellRatio = 1
        self.buffer = 0
        self.marketDemand = 0
        self.electricityPrice = 0
        self.mutex = threading.Lock()
        self.delta = delta
    def getAvailableEnergy(self):
        if not self.running:
            if len(self.clients) == 0:
                return self.buffer
            return self.buffer/float(len(self.clients))
        if len(self.clients) == 0:
            return self.currentCapacity
        return self.currentCapacity/ float(len(self.clients))

    def nUsers(self):
        with self.mutex:
            return len(self.clients)
    def attach(self,client):
        with self.mutex:
            self.clients.append(client)
            return len(self.clients)-1
    def detach(self,client):
        with self.mutex:
            if len(self.clients) == 1:
                self.clients.clear()
                return
            self.clients[client.powerID] = self.clients[-1]
            self.clients.remove(len(self.clients)-1)
            self.clients.append(client)

    def getEnergyPrice(self):
        with self.mutex:
            return self.electricityPrice

    def setValue(self,valueName, value):
        with self.mutex:
            if valueName == "sellRatio":
                self.sellRatio = value;
            elif valueName == "stop":
                self.running = False
            elif valueName == "start":
                self.running = True
            elif valueName == "price":
                self.electricityPrice = value

    def getCurrentData(self):
        with self.mutex:
            return {
                "production":str(self.currentCapacity),
                "consumption":str(self.currentConsumption),
                "sellRatio":str(self.sellRatio),
                "running":str(self.running),
                "buffer":str(self.buffer),
                "demand":str(self.marketDemand)}

    def tick(self):
        if not self.running:
            self.currentCapacity = 0
        self.currentConsumption = 0
        for client in self.clients:
            self.currentConsumption = self.currentConsumption + client.getPurchaseVolume()

        if self.running:
            self.marketDemand = self.currentConsumption / self.currentCapacity
        else:
            self.marketDemand = 1
        self.buffer = self.buffer + self.maxCapacity - self.currentConsumption
        print(self.currentConsumption, "   ", self.marketDemand)
        self.electricityPrice = dataGeneration.calculateDailyEnergyPrice(self.currentCapacity,self.currentConsumption)

        # Update current capacity for the next tick
        self.currentCapacity = self.maxCapacity * self.sellRatio

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
                self.tick()
            sleep(self.delta)
