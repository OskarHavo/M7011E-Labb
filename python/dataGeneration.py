import random
import math
import numpy as np

class PowerConsumption:
    """! Class for the power consumption"""

    def tick(self, date):
        """! Tick function which returns the power consumption based on the calender month to simulate seasons/realistic weather.
        @param date Current date
        @return Current power consumption
        """
        min = [20.0, 19.5, 17.0, 16.0, 14.5, 11.0, 11.0, 12.5, 14.0, 16.0, 18.5, 20.5]
        max = [24.0, 23.5, 20.0, 18.0, 16.0, 13.5, 13.5, 14.5, 15.5, 18.5, 19.5, 23.5]

        currentMonth = date.month - 1  # -1 so January = [0]
        powerConsumption = (min[currentMonth] + random.random() * (max[currentMonth] - min[currentMonth]))
        return powerConsumption

class PowerProduction:
    """! Class for the power production."""
    def __init__(self, startDate, areaCode):
        """! Init.
        @param startDate The start date to refer to.
        @param areaCode The client area code
        """
        self.startDate = startDate
        self.areaCode = areaCode
        self.outOfOrder = False
        self.outOfOrderState = RandomState(areaCode, [0, 1])

    def updateOutOfOrder(self, rand):
        """! Function which simulates the windmills breaking down.
        @param rand A random value.
         """
        if self.outOfOrder:
            # Turn back on with a 5% chance
            if rand < 0.05:
                self.outOfOrder = False
        else:
            # Turn off with a 1% chance
            if rand < 0.01:
                self.outOfOrder = True
        return self.outOfOrder

    def tick(self, date):
        """! Tick function which returns the power production of the windmill based on a sine wave which considers
        the locaiton of the user to provide locational weather.
        @param date Current date.
        @return Current power production
        """
        deltaDate = date - self.startDate  ## Calculate where in the sinewave you are.
        i = deltaDate.days

        self.updateOutOfOrder(self.outOfOrderState.tick())
        if self.outOfOrder:
            return 0

        ## These ranges create a healthy range of the total NetEnergyProduction. (Kan inte randomiza för varje call, man får nog randomiza 1 gång per hus och föra in det som inparameter)
        A = 10  ## Amplitude (Max/Min Value)
        f = 0.01  ## Frequency
        B = self.areaCode  ## Phase  (Adjust for location)
        C = A * 1.5  ## Makes sure the values are not too low and/or negative  ##Check so randomizing the afb values does it make it negative in some config

        powerProduction = A * math.sin(2.0 * math.pi * f * np.float64(i) + B) + C  ## Sinuswave

        return powerProduction


class BuyCalc:
    """! Calculates how much we need to buy based on the current consumption, production and buy ratio
        If the buffer is empty, the value could be higher than anticipated since we need to buy more to achieve the consumption goal.
        This just calculates how much we would like to buy vs how much we want to store.
        If the production is higher than our consumption, the result will be negative to show how much we can either sell or store.
        Requires updates from consumption provider, production provider, available electricity
        Requires previous update from buffer.
    """
    def __init__(self, consumptionProducer, productionProducer, electricity, buffer, buyRatio, clientID):
        """! Init function.
        @param consumptionProducer DataProducer for consumption.
        @param productionProducer DataProducer for production.
        @param electricity EnergyCentral reference.
        @param buffer BufferCalc object.
        @param buyRatio Float number between 0 and 1.
        @param clientID Client user name.
        """
        self.prod = productionProducer
        self.con = consumptionProducer
        self.el = electricity
        self.ratio = buyRatio
        self.result = 0
        self.buffer = buffer
        self.client = clientID

    def setRatio(self, ratio):
        """! Set Ratio.
        @param ratio Float value between 0 and 1
        """
        self.ratio = ratio

    def getRatio(self):
        """! Get Ratio.
        @return Buy ratio.
        """
        return self.ratio

    def currentValue(self):
        """! Get current value.
        @return current Buy value
        """
        return self.result

    def tick(self):
        """! Uses stored electricity in the buffer to calculate how much we need to buy from the power grid.
        Negative values represent a surplus of production energy.
        @return The calculated quota. Same as currentValue()
        """
        electricity = self.el.getAvailableEnergy(self.client)
        wantedConsumption = self.con.currentValue()
        production = self.prod.currentValue()
        currentBuffer = self.buffer.currentValue()

        quota = wantedConsumption - production

        if quota > 0:
            wantToBuy = np.clip(quota * self.ratio, 0, electricity)

            if currentBuffer + wantToBuy >= quota:
                self.buffer.subtract(quota - wantToBuy)
                quota = wantToBuy
            else:
                self.buffer.subtract(currentBuffer)
                quota = np.clip(quota - currentBuffer, 0, electricity)
        self.result = quota
        return quota



class SellRatioCalc:
    """! Calculate how much of the extra energy we can sell to the market.
    Excess energy is represented by a negative number.
    Requires updates from the buy calculator. """
    def __init__(self, buyCalculator, sellRatio):
        """!
        @param buyCalculator BuyCalc
        @param sellRatio Float value between 0 and 1.
        """
        self.sellRatio = sellRatio
        self.buy = buyCalculator
        self.result = 0
        self.blocked = 0

    def setRatio(self, ratio):
        """! Set Ratio.
        @param ratio Float value between 0 and 1.
        """
        if self.blocked > 0:
            ## Can't change value until we are unblocked, then the value will be restored.
            return
        self.sellRatio = ratio

    def getRatio(self):
        """! Get Ratio.
        @return Sell ratio.
        """
        return self.sellRatio

    def currentValue(self):
        """! Get current value.
        @return current sell value.
        """
        return self.result
    def block(self):
        """! Blocks the user from selling for an amount of time."""
        self.blocked = 10
        self.sellRatio = 1

    def tick(self):
        """! Calculate how much electricity we can sell back to the power grid.
        No electricity will be sold if the consumption is larger than the consumption.
        @return The calculated electricity to sell.
        """
        if self.blocked > 0:
            self.blocked = self.blocked - 1
        quota = np.clip(self.buy.currentValue(), self.buy.currentValue(), 0)
        if quota < 0:
            quota = -quota * self.getRatio()
        self.result = quota
        return quota


class BufferCalc:
    """! Calculate how much electricity we can add to the buffer as a function of how much energy we want to sell.
    Requires updates from buy and sell calculator. """

    def __init__(self, buyCalc, sellRatioCalc):
        """! init.
        @param buyCalc BuyCalc
        @param sellRatioCalc SellRatioCalc
        """
        self.buyCalc = buyCalc
        self.buffer = 0
        self.sellRatio = sellRatioCalc

    def subtract(self, value):
        """! Subtract a value from the buffer. """
        self.buffer = np.clip(self.buffer - value, 0, self.buffer)

    def currentValue(self):
        """! Get current value of the buffer. """
        return self.buffer

    def tick(self):
        """! Updates the buffer.
        @return The buffer value
        """
        buyValue = self.buyCalc.currentValue()
        sellValue = self.sellRatio.currentValue()
        if buyValue < 0:
            self.buffer = np.clip(self.buffer + (-buyValue) - sellValue, 0, 100)
        return self.buffer

class ConsumptionChain:
    """!
    This object combines all of the different generator components and puts them in an easy-to-user update cycle.
    We user this in the Windmill class in order to update the state of the windmill.
    """
    def __init__(self, consumptionProducer, productionProducer, powergrid, buyRatio, sellRatio, clientID):
        """!
        @param consumptionProducer  DataProducer for consumption
        @param productionProducer DataProducer for production
        @param powergrid EnergyCentral reference
        @param buyRatio Float value for buy ratio
        @param sellRatio Float value for sell ratio
        @param clientID Client user name
        """
        self.buyCalc = BuyCalc(consumptionProducer, productionProducer, powergrid, None, buyRatio, clientID)
        self.buffer = BufferCalc(self.buyCalc, None)
        self.buyCalc.buffer = self.buffer
        self.sellRatio = SellRatioCalc(self.buyCalc, sellRatio)
        self.buffer.sellRatio = self.sellRatio
        self.prod = productionProducer
        self.con = consumptionProducer
    def tick(self, date):
        """! ?
        @param date The current date.
        @return Production, Consumption, Purchased electricity, Sold electricity and buffer value.
        """
        bruttoProd = self.prod.tick(date)
        self.con.tick(date)
        buySurplus = self.buyCalc.tick()
        sellValue = self.sellRatio.tick()
        buffer = self.buffer.tick()
        return bruttoProd, bruttoProd + buySurplus, np.clip(buySurplus, 0, None), sellValue, buffer

class RandomState:
    """! Utility class for maintaining a deterministic random number generator. We use this to create
    random numbers without disturbing other data structures that also use random numbers. It is also possible
    to warp an input value by some amount, specified by a range.
    """
    def __init__(self, seed, randomRange):
        """! Init.
        @param seed Initial random seed.
        @param randomRange List with range for the randomness.
        """
        self.randomState = None
        self.initRandomState(seed)
        self.currentStateResult = 0
        self.range = randomRange

    def initRandomState(self, seed):
        """! Initialize the instance random state.
        @param seed Initial random seed.
        """
        state = random.getstate()
        random.seed(seed)
        self.randomState = random.getstate()
        random.setstate(state)

    def setRandomState(self):
        """! Activate the instance random state."""
        random.setstate(self.randomState)

    def saveRandomState(self):
        """! Saves the random state. """
        self.randomState = random.getstate()

    def tick(self):
        """! Produce a random number that is unique to this instance. Also save the result locally.
        @return The current state result.
        """
        state = random.getstate()
        self.setRandomState()
        self.currentStateResult = random.random()
        self.saveRandomState()
        random.setstate(state)
        return self.currentStateResult

    def warpSample(self, sample):
        """! Warp a sample based on the current state result.
        @param The sample plus lerped random value
        """
        return sample + lerp(self.range[0], self.range[1], self.currentStateResult)

class DataProducer:
    """! Generic data producer that is user together with PowerConsumption and PowerProduction.
    Could we have user inheritance instead? Yeah, probably, but I don't wanna.

    This also utilized a RandomState object to warp the generated data a little bit before returning it.
    """
    def __init__(self, randState, curveFunction):
        """! Init.
        @param randState RandomState object
        @param curveFunction An object with a tick(date) function
        """
        self.random = randState
        self.func = curveFunction
        self.result = 0
    def currentValue(self):
        """! Get Current Value."""
        return self.result

    def tick(self, currentDateTime):
        """! Produce a new data point based on the set date and time.
        @return the generated output.
        """
        self.random.tick()
        result = self.func.tick(currentDateTime)
        result = self.random.warpSample(result)
        self.result = result
        return result


def lerp(a, b, v):
    """! Linear interpolation, super simple to make buuut I couldn't find one in the standard python libs.
    @param a Start value
    @param b End value
    @paramd v Float value for interpolation
    """
    return a + v * (b - a)


def calculateDailyEnergyPrice(producedEnergy, consumedEnergy):
    """! Create a daily Energy Price based on the demand(consumed energy) and supply(produced energy)

    - High Consumption & Low Producing -> Low Price.
    - Low Consumption & High Producing -> High Price.

    @param producedEnergy Produced energy
    @param consumedEnergy Consumed energy
    @return Calculated energy price between 10 and 50.
    """
    basePrice = 10.0
    maxPrice = 50.0

    ## Introduce price cap to combat infinite energy prices when windmills break.
    if (producedEnergy == 0):
        dailyElectrictyPrice = maxPrice

    else:
        demandSupplyFactor = consumedEnergy / producedEnergy

        dailyElectrictyPrice = basePrice * demandSupplyFactor

        if dailyElectrictyPrice > maxPrice:
            dailyElectrictyPrice = maxPrice
    return dailyElectrictyPrice
