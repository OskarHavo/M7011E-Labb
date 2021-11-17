import random
import time

from dataGeneration import *

class EnergyDataPoint:
    def __init__(self):
        Date = ""
        ProducedEnergy = 0
        ConsumedEnergy = 0
        EnergyPrice = 0
        EnergySurplus = False
        NetEnergyProduction = 0


class Household:
    def __init__(self):
        D = 0
        EnergyBuffer = 0  # TODO
        EnergyBuyingRatio = 0  # TODO
        EnergySellingRatio = 0  # TODO
        DataPoints = []

datapoints = []
households = []

def initializeModel(howManyHouseholds, datapointsForHowManyYears, startDate):
    random.seed(random.randint(0,100000))
    households = createHouseHolds(howManyHouseholds, datapointsForHowManyYears,startDate)

def playModel():
    # TODO Load first date and load each households data for that date.
    # TODO Every 5seconds move to to next date
    # TODO for each date, add datapoint.NetEnergyProduction to Household.Buffer
    return

def createHouseHolds(howManyHouseholds, datapointsForHowManyYears, startDate):
    numberOfYears = datapointsForHowManyYears
    numberOfHouseholds = howManyHouseholds
    newHouseholdList = []

    for i in range(0, numberOfHouseholds):
        household = Household()
        household.ID = i
        household.EnergyBuffer = 0
        household.EnergyBuyingRatio = 0.5
        household.EnergySellingRatio = 0.5
        household.DataPoints = createDataPoints(numberOfYears, startDate)

        newHouseholdList.append(household)
    return newHouseholdList

def createDataPoints(datapointsForHowManyYears, startDate):
    generatedDateRange = createDateRange(startDate, datapointsForHowManyYears)
    numberOfDates = len(generatedDateRange)

    # Generate	Data
    # Wind is gradual and season like -> Sine Wave.HouseholdPower is consistent(seasonal variation might occur though) -> Randomfloats in range.
    generatedEnergyProduction = generateSineWaveFloats(10.0, 20.0, numberOfDates)
    generatedEnergyConsumption = randomizeSeasonalFloats(startDate,numberOfDates)  # generateNormalDistibutionFloats(numberOfDates, numberOfYears)
    # generatedDailyEnergyPrice, generatedDailySurplusStatus := generateEnergyPrice(generatedEnergyConsumption,generatedEnergyProduction)

    print("Length of generatedEnergyProduction", len(generatedEnergyProduction))
    print("Length of generatedEnergyConsumption", len(generatedEnergyConsumption))
    # print("Length of generatedDailyEnergyPrice", len(generatedDailyEnergyPrice))
    print("Length of generatedDateRange", len(generatedDateRange))
    # fmt.Println("Length of generatedDailySurplusStatus", len(generatedDailySurplusStatus))

    newDatapointsList = []
    daysOfOutage = 0

    # Add Date and ProducedEnergy into structs and add them to the struct list.
    for i in range(0,numberOfDates):
        datapoint = EnergyDataPoint()
        datapoint.Date = generatedDateRange[i]

        # If Windmill breaks, an outage will occur for 2-5 days.
        if daysOfOutage == 0 and isWindmillBroken():
            daysOfOutage = random.randint(3, 6)

        # If Windmill broken, produced energy will plummet (Still a value so no infinite electricity price)
        # Otherwise take from datalist
        if daysOfOutage != 0:
            datapoint.ProducedEnergy = 0.0
            daysOfOutage = daysOfOutage - 1
        else:
            datapoint.ProducedEnergy = generatedEnergyProduction[i]

        datapoint.ConsumedEnergy = generatedEnergyConsumption[i]
        datapoint.EnergyPrice, datapoint.EnergySurplus = calculateDailyEnergyPrice(datapoint.ProducedEnergy,
                                                                                   datapoint.ConsumedEnergy)
        datapoint.NetEnergyProduction = calculateNetEnergyProduction(datapoint.ProducedEnergy, datapoint.ConsumedEnergy)

        print("Date: ", datapoint.Date, " ProducedEnergy:  ", datapoint.ProducedEnergy,
              " ConsumedEnergy:  ", datapoint.ConsumedEnergy, " EnergyPrice:  ", datapoint.EnergyPrice,
              )

        # " EnergySurplus:  ", datapoint.EnergySurplus, " NetEnergyProduction:  ", datapoint.NetEnergyProduction)

        # fmt.Println(datapoint.Date, "Price:",calculateConsumerPrice(datapoint.ProducedEnergy, datapoint.ConsumedEnergy, datapoint.EnergyPrice,datapoint.EnergySurplus))
        newDatapointsList.append(datapoint)
    return newDatapointsList


def updateListAfterDowntime(datapoint):
    datapoint.ProducedEnergy = 0
    datapoint.EnergySurplus = isSurplus(datapoint.ConsumedEnergy, datapoint.ProducedEnergy)
    datapoint.NetEnergyProduction = calculateNetEnergyProduction(datapoint.ProducedEnergy, datapoint.ConsumedEnergy)

def getNumberOfDays(numberOfYears):
    numberOfDates = (numberOfYears * 365) + 1
    return numberOfDates

# Calculate the Final Consumer Price Per Day.
def calculateConsumerPrice(producedEnergy, consumedEnergy, energyPrice, isSurplus):
    # If surplus, no need to buy energy.
    if isSurplus:
        consumerPrice = 0.0
        return consumerPrice
    else:
        # Calculate the energy missing and buy it for the daily price.
        consumerPrice = (consumedEnergy - producedEnergy) * energyPrice
        return consumerPrice

def isWindmillBroken():
    randomInteger = random.randint(1, 500)

    # 1/500 Chance for Windmill to break.
    if randomInteger == 42:
        return True
    else:
        return False

# REST API
def getWindSpeed(date):
    # take datapoint with date as key -> windenergy for that day as value
    # divide value with value x to get the wind speed.

    windSpeed = 1.0445
    return windSpeed


def getNumberOfDays(numberOfYears):
    numberOfDates = (numberOfYears * 365) + 1
    return numberOfDates


def getElectricityConsumption(date):
    # take datapoint with date as key -> consumption for that day as value

    electricityConsumption = 1.0445
    return electricityConsumption


def getElectricityPrice(date):
    # take datapoint with date as key -> price for that day as value

    electricityPrice = 1.0445
    return electricityPrice

