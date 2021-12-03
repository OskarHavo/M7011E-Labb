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
        self.syncMutext = threading.Lock()
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
        with self.syncMutext:
            if valueName == "buyRatio":
                self.chain.buyCalc.setRatio(float(value))
                return
            elif valueName == "sellRatio":
                self.chain.sellRatio.setRatio(float(value))
                return

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
        self.date = datetime.datetime.now()

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
        with self.syncMutext:
            self.updateTime()
            bruttoProd, consumption, buySurplus, sellValue, buffer = self.chain.tick(self.date)
            bruttoProd = str(bruttoProd)
            consumption = str(consumption)
            buySurplus = str(buySurplus)
            sellValue = str(sellValue)
            buffer = str(buffer)
            year = str(self.date.year)
            month = str(self.date.month)
            day = str(self.date.day)
            hour = str(self.date.hour)
            minute = str(self.date.minute)
            second = str(self.date.second)
            return {"production": bruttoProd, "consumption": consumption, "powerToBuy": buySurplus, "powerToSell": sellValue, "buffer": buffer, "year":year,"month":month,"day":day,"hour":hour,"minute":minute,"second":second}
