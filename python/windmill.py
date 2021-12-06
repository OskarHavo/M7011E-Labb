import datetime
import threading
import dataGeneration


class ProductionNode:
    def __init__(self, user, postalCode, productionRandomRange, consumptionRandomRange, powerplant):
        self.postalCode = postalCode
        self.date = datetime.datetime.now()
        self.outOfOrder = False
        self.user = user
        self.powerplant = powerplant
        self.syncMutex = threading.Lock()
        powerplant.attach()

        productionProducer = dataGeneration.DataProducer(
            dataGeneration.RandomState(postalCode, productionRandomRange),
            dataGeneration.PowerProduction(datetime.datetime(1970, 1, 1), postalCode)
        )
        consumptionProducer = dataGeneration.DataProducer(
            dataGeneration.RandomState(postalCode, productionRandomRange),
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
            else:
                print("Received some weird value ", valueName, value)

    def __del__(self):
        self.powerplant.detach()

    def getName(self):
        return self.user

    def getBuffer(self):
        return self.energyBuffer

    def getProduction(self):
        return self.currentProduction

    def getConsumption(self):
        return self.currentConsumption

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
            grossProduction, consumption, powerToBuy, powerToSell, buffer = self.chain.tick(self.date)
            grossProduction = str(grossProduction)
            consumption = str(consumption)
            powerToBuy = str(powerToBuy)
            powerToSell = str(powerToSell)
            buffer = str(buffer)
            buy = str(self.chain.buyCalc.ratio)
            sell = str(self.chain.sellRatio.sellRatio)
            return {"production": grossProduction, "consumption": consumption, "powerToBuy": powerToBuy, "powerToSell": powerToSell, "buffer": buffer,"buyRatio":buy,"sellRatio":sell,"timestamp": str(self.date)}#, "year":year,"month":month,"day":day,"hour":hour,"minute":minute,"second":second}
