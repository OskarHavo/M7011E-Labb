import datetime
import random
import threading
import dataGeneration

from EnergyCentral import EnergyCentral

class WindmillQueue:
    def __init__(self, maxLen = 10):
        self.queue = []
        self.sem = threading.Semaphore(0)
        self.mtx = threading.Lock()
        self.maxLen = maxLen
    def get(self):
        self.sem.acquire()
        with self.mtx:
            return self.queue.pop(0)
    def put(self,data):
        with self.mtx:
            self.queue.append(data)
            if self.maxLen < len(self.queue):
                self.queue.pop()
            self.sem.release()


class ProductionNode:
    def __init__(self, user, postalCode, productionRandomRange, consumptionRandomRange, powerplant):
        self.postalCode = postalCode
        self.date = datetime.datetime.now()
        self.outOfOrder = False
        self.user = user
        self.powerplant = powerplant
        self.syncMutex = threading.Lock()
        self.powerID = powerplant.attach(self)
        self.currentPurchase = 0
        self.energyBuffer = 0
        self.currentProduction = 0
        self.currentPrice = 15.0
        self.timeData = []

        productionProducer = dataGeneration.DataProducer(
            dataGeneration.RandomState(postalCode+random.random(), productionRandomRange),
            dataGeneration.PowerProduction(datetime.datetime(1970, 1, 1), postalCode)
        )
        consumptionProducer = dataGeneration.DataProducer(
            dataGeneration.RandomState(postalCode+random.random(), productionRandomRange),
            dataGeneration.PowerConsumption()
        )
        self.chain = dataGeneration.ConsumptionChain(consumptionProducer, productionProducer, self.powerplant, 0.5, 0.5)

    def setValue(self, valueName, value):
        with self.syncMutex:
            if valueName == "buyRatio":
                self.chain.buyCalc.setRatio(float(value))
                return
            elif valueName == "sellRatio":
                self.chain.sellRatio.setRatio(float(value))
                return
            elif valueName == "block":
                # A user can 'technically' block themselves
                self.chain.sellRatio.block()
            else:
                print("Received some weird value ", valueName, value)

    def __del__(self):
        self.powerplant.detach(self)

    def getName(self):
        with self.syncMutex:
            return self.user

    def getBuffer(self):
        with self.syncMutex:
            return self.energyBuffer

    def getProduction(self):
        with self.syncMutex:
            return self.currentProduction

    def getPurchaseVolume(self):
        with self.syncMutex:
            return self.currentPurchase
    def getBlockStatus(self):
        with self.syncMutex:
            return self.chain.sellRatio.blocked > 0

    def getStream(self):
        self.timeData.append(WindmillQueue)
        return self.timeData[-1]

    def updateTime(self):
        date = datetime.datetime.now()
        formattedDate = date - datetime.timedelta(microseconds=date.microsecond) # Ensures only 2 digits for seconds
        self.date = formattedDate

    def updateOutOfOrder(self, rand):
        if self.outOfOrder:
            # Turn back on with a 20% chance
            if rand < 0.2:
                self.outOfOrder = False
        else:
            # Turn off with a 10% chance
            if rand < 0.1:
                self.outOfOrder = True
        return self.outOfOrder

    def tick(self):
        with self.syncMutex:
            self.updateTime()
            self.currentProduction, consumption, self.currentPurchase, powerToSell, buffer = self.chain.tick(self.date)
            data = {
                "production": str(self.currentProduction),
                "consumption": str(consumption),
                "powerToBuy": str(self.currentPurchase),
                "powerToSell": str(powerToSell),
                "buffer": str(buffer),
                "buyRatio":str(self.chain.buyCalc.ratio),
                "sellRatio":str(self.chain.sellRatio.getRatio()),
                "timestamp": str(self.date),
                "windspeed": str(self.currentProduction/3.0),
                "electricityPrice": str(self.powerplant.getEnergyPrice()),
                "blocked": str(self.chain.sellRatio.blocked > 0)}
            for port in self.timeData:
                port.put(data)
            return data
