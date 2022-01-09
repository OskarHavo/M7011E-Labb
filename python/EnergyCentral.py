import random
import threading
from time import sleep
import dataGeneration
import datetime

class EnergyCentral:
    def __init__(self, maxCapacity,delta):
        self.capacityModifier = 1
        self.maxCapacity = maxCapacity
        self.currentCapacity = 0
        self.currentConsumption = 0
        self.clients = {}
        self.running = 0 # 0 = Stopped 1-9 = Starting 10 = Running
        self.sellRatio = 1
        self.buffer = 0
        self.marketDemand = 0
        self.modeledElectricityPrice = 0
        self.electricityPrice = 15.0
        self.blackoutRandState = dataGeneration.RandomState(random.random(),[0,1])
        self.date = datetime.datetime.now()
        self.mutex = threading.Lock()
        self.delta = delta
    def getAvailableEnergy(self,user):
        if self.clients[user]["powerOutage"]:
            return 0
        if self.running < 10:
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
            self.clients[client] = {"powerOutage":False}
    def detach(self,client):
        with self.mutex:
            if client in self.clients:
                del self.clients[client]

    def getEnergyPrice(self):
        with self.mutex:
            return self.electricityPrice
    def getBlackoutStatus(self):
        with self.mutex:
            return self.blackout

    def setValue(self,valueName, value):
        with self.mutex:
            if valueName == "sellRatio":
                self.sellRatio = value;
            elif valueName == "stop":
                self.running = 0
            elif valueName == "start":
                self.running = 1
            elif valueName == "powerplantproduction":
                self.capacityModifier = value;
                if self.capacityModifier == 0:
                    self.running = 0
                elif self.running == 0:
                    self.running = 1
            elif valueName == "marketRatio":
                self.sellRatio = value
            elif valueName == "currentelectricityprice":
                self.electricityPrice = value

    def updateTime(self):
        date = datetime.datetime.now()
        formattedDate = date - datetime.timedelta(microseconds=date.microsecond) # Ensures only 2 digits for seconds
        self.date = formattedDate

    def getCurrentData(self):
        with self.mutex:
            return {
                "production":str(self.currentCapacity),
                "consumption":str(self.currentConsumption),
                "sellRatio":str(self.sellRatio),
                "running":str(self.running),
                "buffer":str(self.buffer),
                "modeledPrice":str(self.modeledElectricityPrice),
                "price":str(self.electricityPrice),
                "timestamp":str(self.date),
                "demand":str(self.marketDemand),
                "maxCapacityPercentage":str(self.capacityModifier),
                "maxCapacity":str(self.maxCapacity)}

    def updatePowerOutage(self):
        for client in self.clients:
            rn = self.blackoutRandState.tick()
            if self.clients["powerOutage"]:
                # Turn back on with a 20% chance
                if rn < 0.2:
                    self.clients["powerOutage"] = False
            else:
                # Turn off with a 10% chance
                if rn < 0.1:
                    self.clients["powerOutage"] = True

    def tick(self):
        self.updateTime()
        self.updatePowerOutage()
        self.currentConsumption = 0
        for client in self.clients:
            if not self.clients[client]["powerOutage"]:
                self.currentConsumption = self.currentConsumption + client.getPurchaseVolume()

        cap = self.capacityModifier*self.maxCapacity

        self.currentCapacity = self.sellRatio*cap
        if self.running < 10:
            self.currentCapacity = self.buffer
            if self.running > 0:
                self.running = self.running + 1
            self.buffer = self.buffer - self.currentConsumption
        else:
            self.buffer = self.buffer + cap - self.currentConsumption

        print(self.currentConsumption, "   ", self.marketDemand, "   ", self.currentCapacity, "   ", self.running)
        self.marketDemand = 0
        if self.currentCapacity > 0:
            self.marketDemand = (self.currentConsumption / self.currentCapacity)*100.0




        self.modeledElectricityPrice = dataGeneration.calculateDailyEnergyPrice(self.currentCapacity, self.currentConsumption)


    def stop(self):
        with self.mutex:
            self.running = 0

    def run(self,socketio):
        with self.mutex:
            self.running = 1
        while True:
            with self.mutex:
                if self.running == 0:
                    break
                self.tick()
            socketio.sleep(self.delta)
