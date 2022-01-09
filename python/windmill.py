import datetime
import random
import threading
import dataGeneration


class WindmillQueue:
    def __init__(self, maxLen=10):
        self.queue = []  # FIFO queue of datapoints

        self.condition = threading.Condition()
        self.queueMutex = threading.Lock()
        self.maxLen = maxLen

    def getNext(self, timestamp):

        ## Check if the timestamp is newer then all datapoints in the queue
        ## There is no point in iterating through all data samples if we don't want to return any of them
        with self.queueMutex:
            newTime = datetime.datetime.strptime(self.queue[-1]["timestamp"], "%Y-%m-%d %H:%M:%S")

            if newTime <= timestamp:
                ## The timestamp is newer than the most recent update. Return nothing.
                return None, None

        ## The datapoint we seek is neither the newest or the oldest. find which one and return it.
        with self.queueMutex:
            for i in range(0, len(self.queue)):
                newtime = datetime.datetime.strptime(self.queue[i]["timestamp"], "%Y-%m-%d %H:%M:%S")
                if newtime > timestamp:
                    ## Return all samples that are newer than the given timestamp
                    return self.queue[i:], self.queue[-1]["timestamp"]

    def put(self, data):
        with self.queueMutex:
            self.queue.append(data)
            if self.maxLen < len(self.queue):
                self.queue.pop(0)
            with self.condition:
                self.condition.notify_all()  ## Notify any thread that is waiting for a new value


class ProductionNode:
    def __init__(self, user, postalCode, productionRandomRange, consumptionRandomRange, powerplant):
        self.postalCode = postalCode
        self.date = datetime.datetime.now()
        self.outOfOrder = False
        self.user = user
        self.powerplant = powerplant
        self.syncMutex = threading.Lock()
        self.currentPurchase = 0
        self.energyBuffer = 0
        self.currentProduction = 0
        self.currentPrice = 15.0
        self.timeData = WindmillQueue()
        self.callbackBuffer = []

        productionProducer = dataGeneration.DataProducer(
            dataGeneration.RandomState(postalCode + random.random(), productionRandomRange),
            dataGeneration.PowerProduction(datetime.datetime(1970, 1, 1), postalCode)
        )
        consumptionProducer = dataGeneration.DataProducer(
            dataGeneration.RandomState(postalCode + random.random(), consumptionRandomRange),
            dataGeneration.PowerConsumption()
        )
        self.chain = dataGeneration.ConsumptionChain(consumptionProducer, productionProducer, self.powerplant, 0.5, 0.5,
                                                     user)
        powerplant.attach(self)

    def setValue(self, valueName, value=None):
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

    def getNext(self, timestamp, callback=None, *callbackargs):
        with self.syncMutex:
            data, timestamp = self.timeData.getNext(timestamp)
            if not data:
                self.callbackBuffer.append((callback, callbackargs))
            return data, timestamp

    def updateTime(self):
        date = datetime.datetime.now()
        formattedDate = date - datetime.timedelta(microseconds=date.microsecond)  # Ensures only 2 digits for seconds
        self.date = formattedDate

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
                "buyRatio": str(self.chain.buyCalc.ratio),
                "sellRatio": str(self.chain.sellRatio.getRatio()),
                "timestamp": str(self.date),
                "windspeed": str(self.currentProduction / 3.0),
                "electricityPrice": str(self.powerplant.getEnergyPrice()),
                "blocked": str(self.chain.sellRatio.blocked > 0)}
            self.timeData.put(data)
            for callback in self.callbackBuffer:
                callback[0]([data], self.date, *callback[1])
            self.callbackBuffer = []
            return data
