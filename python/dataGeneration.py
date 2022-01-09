import datetime
import random
import math
import numpy as np
from random import randrange
from EnergyCentral import EnergyCentral

class PowerConsumption:
    def tick(self,date):
        min = [20.0, 19.5, 17.0, 16.0, 14.5, 11.0, 11.0, 12.5, 14.0, 16.0, 18.5, 20.5]
        max = [24.0, 23.5, 20.0, 18.0, 16.0, 13.5, 13.5, 14.5, 15.5, 18.5, 19.5, 23.5]

        currentMonth = date.month - 1  # -1 so January = [0]
        powerConsumption = (min[currentMonth] + random.random() * (max[currentMonth] - min[currentMonth]))
        return powerConsumption
class PowerProduction:
    def __init__(self,startDate,areaCode):
        self.startDate = startDate
        self.areaCode = areaCode
    def tick(self,date):
        deltaDate = date - self.startDate  # Calculate where in the sinewave you are.
        i = deltaDate.days

        # Placeholder
        if True:


        # Det här går inte och du vet varför. Fixa utan att ändra i EnergyCentral
        #if EnergyCentral.getBlackoutStatus() == False:



            # These ranges create a healthy range of the total NetEnergyProduction. (Kan inte randomiza för varje call, man får nog randomiza 1 gång per hus och föra in det som inparameter)
            A = 10  # random.randint(10, 12)  # Amplitude (Max/Min Value)
            f = 0.01  # Frequency
            B = self.areaCode  # Phase  (Adjust for location)
            C = A * 1.5  # Makes sure the values are not too low and/or negative  ##Check so randomizing the afb values does it make it negative in some config

            powerProduction = A * math.sin(2.0 * math.pi * f * np.float64(i) + B) + C  # Sinuswave
        else:
            # If blackout, randomize 4 areacodes and set the production which is sent to these areas to zero.
            affectedPostalCodes = []

            affectedPostalCodes.append(randrange(10))
            affectedPostalCodes.append(randrange(10))
            affectedPostalCodes.append(randrange(10))
            affectedPostalCodes.append(randrange(10))

            if self.areaCode in affectedPostalCodes:
                powerProduction = 0
            else:
                A = 10
                f = 0.01
                B = self.areaCode
                C = A * 1.5 

                powerProduction = A * math.sin(2.0 * math.pi * f * np.float64(i) + B) + C  # Sinuswave

        return powerProduction

# Calculates how much we need to buy based on the current consumption, production and buy ratio
# If the buffer is empty, the value could be higher than anticipated since we need to buy more to achieve the consumption goal.
# This just calculates how much we would like to buy vs how much we want to store.
# If the production is higher than our consumption, the result will be negative to show how much we can either sell or store.
# Requires updates from consumption provider, production provider, available electricity
# Requires previous update from buffer
class BuyCalc:
    def __init__(self,consumptionProducer,productionProducer,electricity,buffer,buyRatio):
        self.prod = productionProducer
        self.con = consumptionProducer
        self.el = electricity
        self.ratio = buyRatio
        self.result = 0
        self.buffer = buffer


    def setRatio(self,ratio):
        self.ratio = ratio

    def getRatio(self):
        return self.ratio

    def currentValue(self):
        return self.result

    # Uses stored electricity in the buffer to calculate how much we need to buy from the power grid.
    # Negative values represent a surplus of production energy.
    def tick(self):
        electricity = self.el.getAvailableEnergy()
        wantedConsumption = self.con.currentValue()
        production = self.prod.currentValue()
        currentBuffer = self.buffer.currentValue()

        quota = wantedConsumption-production

        if quota > 0:
            wantToBuy = np.clip(quota * self.ratio,0,electricity)

            if currentBuffer+wantToBuy >= quota:
                self.buffer.subtract(quota - wantToBuy)
                quota = wantToBuy
            else:
                self.buffer.subtract(currentBuffer)
                quota = np.clip(quota-currentBuffer,0,electricity)
        self.result = quota
        return quota


# Calculate how much of the extra energy we can sell to the market.
# Excess energy is represented by a negative number.
# Requries updates from the buy calculator
class SellRatioCalc:
    def __init__(self,buyCalculator,sellRatio):
        self.sellRatio = sellRatio
        self.buy = buyCalculator
        self.result = 0
        self.blocked = 0

    def setRatio(self,ratio):
        if self.blocked > 0:
            # Can't change value until we are unblocked, then the value will be restored.
            return
        self.sellRatio = ratio
    def getRatio(self):
        return self.sellRatio
    def currentValue(self):
        return self.result

    def block(self):
        self.blocked = 10
        self.sellRatio = 1

    # Calculate how much electricity we can sell back to the power grid.
    # No electricity will be sold if the consumption is larger than the consumption.
    def tick(self):
        if self.blocked > 0:
            self.blocked = self.blocked - 1
        quota = np.clip(self.buy.currentValue(),self.buy.currentValue(),0)
        if quota < 0:
            quota = -quota*self.getRatio()
        self.result = quota
        return quota

# Calulate how much electricity we can add to the buffer as a function of how much energy we want to sell.
# Requires updates from buy and sell calculator
class BufferCalc:
    def __init__(self,buyCalc,sellRatioCalc):
        self.buyCalc = buyCalc
        self.buffer = 0
        self.sellRatio = sellRatioCalc
    def subtract(self, value):
        self.buffer = np.clip(self.buffer - value,0,self.buffer)
    def currentValue(self):
        return self.buffer
    def tick(self):
        buyValue = self.buyCalc.currentValue()
        sellValue = self.sellRatio.currentValue()
        if buyValue < 0:
            self.buffer = np.clip(self.buffer + (-buyValue)-sellValue,0,100)
        return self.buffer


class ConsumptionChain:
    def __init__(self,consumptionProducer,productionProducer, powergrid,buyRatio,sellRatio):
        self.buyCalc = BuyCalc(consumptionProducer,productionProducer,powergrid,None,buyRatio)
        self.buffer = BufferCalc(self.buyCalc,None)
        self.buyCalc.buffer = self.buffer
        self.sellRatio = SellRatioCalc(self.buyCalc,sellRatio)
        self.buffer.sellRatio = self.sellRatio
        self.prod = productionProducer
        self.con = consumptionProducer


    def tick(self,date):
        bruttoProd = self.prod.tick(date)
        consumption = self.con.tick(date)
        buySurplus = self.buyCalc.tick()
        sellValue = self.sellRatio.tick()
        buffer = self.buffer.tick()
        return bruttoProd,bruttoProd+buySurplus,np.clip(buySurplus,0,None),sellValue,buffer


class RandomState:
    def __init__(self, seed, randomRange):
        self.randomState = None
        self.initRandomState(seed)
        self.currentStateResult = 0
        self.range = randomRange

    ## Initialize the instance random state
    def initRandomState(self, seed):
        state = random.getstate()
        random.seed(seed)
        self.randomState = random.getstate()
        random.setstate(state)

    ## Activate the instance random state
    def setRandomState(self):
        random.setstate(self.randomState)

    ## Save the random state
    def saveRandomState(self):
        self.randomState = random.getstate()

    ## Produce a random number that is unique to this instance. Also save the result locally
    def tick(self):
        state = random.getstate()
        self.setRandomState()
        self.currentStateResult = random.random()
        self.saveRandomState()
        random.setstate(state)
        return self.currentStateResult

    # Warp a sample based on the current state result
    def warpSample(self, sample):
        return sample + lerp(self.range[0], self.range[1], self.currentStateResult)

class DataProducer:
    def __init__(self,randState,curveFunction):
        self.random = randState
        self.func = curveFunction
        self.result = 0

    def currentValue(self):
        return self.result

    # Produce a new data point based on the set date and time
    def tick(self,currentDateTime):
        self.random.tick()
        result = self.func.tick(currentDateTime)
        result = self.random.warpSample(result)
        self.result = result
        return result

def lerp(a, b, v):
    return a + v * (b - a)

# Create a daily Energy Price based on the demand(consumed energy) and supply(produced energy)
# Returns the price, surplus status and netenergyproduction
def calculateDailyEnergyPrice(producedEnergy, consumedEnergy):
    # High Consumption & Low Producing -> Low Price
    # Low Consumption & High Producing -> High Price

    basePrice = 10.0
    maxPrice = 50.0

    # Introduce price cap to combat infinite energy prices when windmills break.
    if (producedEnergy == 0):
        dailyElectrictyPrice = maxPrice

    else:
        demandSupplyFactor = consumedEnergy / producedEnergy

        dailyElectrictyPrice = basePrice * demandSupplyFactor

        if dailyElectrictyPrice > maxPrice:
            dailyElectrictyPrice = maxPrice
    return dailyElectrictyPrice
