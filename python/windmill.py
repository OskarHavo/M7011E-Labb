import datetime
import random
import threading
import dataGeneration

from EnergyCentral import EnergyCentral

class WindmillQueue:
    def __init__(self, maxLen = 10):
        self.queue = [] # FIFO queue of datapoints

        self.condition = threading.Condition()
        #self.conditionMutex = threading.RLock()
        self.queueMutex = threading.Lock()
        self.maxLen = maxLen
    def getNext(self,timestamp):

        # Check if the timestamp is older than all datapoints in the queue
        with self.queueMutex:
            # 2022-01-07 10:59:56
            newTime = datetime.datetime.strptime(self.queue[0]["timestamp"],"%Y-%m-%d %H:%M:%S")
            # If timestamp is older than all samples in queue
            if newTime > timestamp:
                return self.queue[0],newTime

        # Check if the timestamp is newer then all datapoints in the queue
        with self.condition:

            self.queueMutex.acquire()   # Manually aquire the queue lock
            newTime = datetime.datetime.strptime(self.queue[-1]["timestamp"],"%Y-%m-%d %H:%M:%S")

            if newTime <= timestamp:
                # The timestamp is newer. We need to wait for a windmill update
                self.queueMutex.release()   # Release queue mutex so a new value can be added
                self.condition.wait() # Wait to be unlocked byt the windmill

                with self.queueMutex:   # Yes, we need to lock the queue mutex again because we had to wait
                    # The newly added data will always be valid since it has a newer timestamp.
                    newTime = self.queue[-1]["timestamp"]
                    return self.queue[-1],newTime
            else:
                self.queueMutex.release()

        # The datapoint we seek is neither the newest or the oldest
        with self.queueMutex:
            for d in self.queue:
                newtime = datetime.datetime.strptime(d["timestamp"],"%Y-%m-%d %H:%M:%S")
                if newtime  > timestamp:
                    return d,newtime

    def put(self,data):
        with self.queueMutex:
            self.queue.append(data)
            if self.maxLen < len(self.queue):
                self.queue.pop(0)
            with self.condition:
                self.condition.notify_all() # Notify any thread that is waiting for a new value


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
        self.timeData = WindmillQueue()

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

    def getNext(self,timestamp):
        return self.timeData.getNext(timestamp)

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
            self.timeData.put(data)
            return data