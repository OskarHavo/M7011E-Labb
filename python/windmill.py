import datetime
import random
import threading
import dataGeneration


class WindmillQueue:
    """! The windmill queue stores some of the most recent updates in a FIFO queue so that clients always can get
    some fresh data when they log in :)

    It is also used when a client requests some data. We either return the n newest samples or nothing at all.
    """
    def __init__(self, maxLen=10):
        """! Init function.
        @param maxLen The max length of samples to store.
        """
        self.queue = []  # FIFO queue of datapoints
        self.queueMutex = threading.Lock()
        self.maxLen = maxLen

    def getNext(self, timestamp):
        """! Retrieve all data samples with a newer timestamp in the FIFO queue.
        @param timestamp The current timestamp
        @return A list of data samples and the timestamp for the newest sample. If no samples can be retrieved, None, None is returned.
        """
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
        """! Store a new sample in the FIFO queue.
        @param data The data sample to store.
        """
        with self.queueMutex:
            self.queue.append(data)
            if self.maxLen < len(self.queue):
                self.queue.pop(0)

class Windmill:
    """! This is the actual windmill class. It is responsible for updating the state of a windmill and produces the
    output energy.
    """
    def __init__(self, user, postalCode, productionRandomRange, consumptionRandomRange, powerplant):
        """! Init function.
            @param user  Username
            @param postalCode  Postal code
            @param productionRandomRange  A list range for the production random range. E.g. [-1,1]
            @param consumptionRandomRange  A list range for the consumption random range. E.g. [-1,1]
            @param powerplant  A reference to an EnergyCentral instance
            """
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
        """! Set value to Production Node."""
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
        """! Delete Production Node. """
        self.powerplant.detach(self)


    def getPurchaseVolume(self):
        """! Get current purchase volume from Production Node.
        @return Current electricity purchase amount.
        """
        with self.syncMutex:
            return self.currentPurchase


    def getBlockStatus(self):
        """! Get block status from Production Node.
        @return True if this windmill is blocked.
        """
        with self.syncMutex:
            return self.chain.sellRatio.blocked > 0


    def getNext(self, timestamp, callback=None, *callbackargs):
        """! This tries to fetch some data from the windmill. If no data can be retrieved, the windmill will
        store a callback function in a buffer and call it upon the next update.
        @param timestamp Timestamp used to determine which samples the client has already fetched before.
        @param callback Optional callback function used for buffering requests. The callback must accept a list of data
            and a timestamp.
        @param callbackargs Optional callback args.
        @return Data in form of a list and a timestamp of the newest sample or nothing at all.
        """
        with self.syncMutex:
            data, timestamp = self.timeData.getNext(timestamp)
            if not data:
                self.callbackBuffer.append((callback, callbackargs))
            return data, timestamp


    def updateTime(self):
        """! Update the timestamp. """
        date = datetime.datetime.now()
        formattedDate = date - datetime.timedelta(microseconds=date.microsecond)  # Ensures only 2 digits for seconds
        self.date = formattedDate


    def tick(self):
        """! Update the windmill. This will also iterate through all request callbacks and notify them.
        @return The newly generated data sample. This only here for legacy reasons, I think.
        """
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

            # Iterate through all callbacks.
            for callback in self.callbackBuffer:
                callback[0]([data], self.date, *callback[1])
            self.callbackBuffer = [] # Empty the callback buffer because we have handled all requests.

            return data
