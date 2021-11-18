import random
import time

from dataGeneration import *

class Household:
    def __init__(self):
        ID = 0
        EnergyBuffer = 0  # TODO
        EnergyBuyingRatio = 0  # TODO
        EnergySellingRatio = 0  # TODO
        DataPoints = dict() # DataPoints[date] = {producedEnergy, consumedEnergy,energyPrice,energySurplus,netEnergyProduction}

households = []

def initializeModel(howManyHouseholds, datapointsForHowManyYears, startDate):
    random.seed(random.randint(0,100000))
    households = createHouseHolds(howManyHouseholds, datapointsForHowManyYears,startDate)

    queryDate = "2023-12-31"
    for household in households:
        print("\n")
        print("HOUSEHOlD: " + str(household.ID) + " at the date: " + queryDate)
        print("Windspeed: " + str(getHouseholdWindSpeed(household, queryDate)) + " m/s")
        print("EnergyProduction: " + str(getHouseholdEnergyProduction(household, queryDate)) + " kWh")
        print("EnergyConsumption: " + str(getHouseholdEnergyConsumption(household, queryDate)) + " kWh")
        print("EnergyNetProduction :" + str(getHouseholdNetEnergyProduciton(household, queryDate)) + " kWh")
        print("EnergySurplus is: " + str(getHouseholdEnergySurplus(household, queryDate)))
        print("EnergyPrice: " + str(getHouseholdEnergyPrice(household, queryDate)) + " kr")

    #printDataPoint(households[0], "2023-12-31")

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

    datapointsForDate = dict()
    daysOfOutage = 0

    # Add Date and ProducedEnergy into structs and add them to the struct list.
    for i in range(0,numberOfDates):

        # If Windmill breaks, an outage will occur for 2-5 days.
        if daysOfOutage == 0 and isWindmillBroken():
            daysOfOutage = random.randint(3, 6)

        # If Windmill broken, produced energy will plummet (Still a value so no infinite electricity price)
        # Otherwise take from datalist
        if daysOfOutage != 0:
            producedEnergy = 0.0
            daysOfOutage = daysOfOutage - 1
        else:
            producedEnergy = generatedEnergyProduction[i]

        date = str(generatedDateRange[i])
        consumedEnergy = generatedEnergyConsumption[i]
        energyPrice, energySurplus = calculateDailyEnergyPrice(producedEnergy, consumedEnergy)
        netEnergyProduction = calculateNetEnergyProduction(producedEnergy, consumedEnergy)

        print("Date:", date, "ProducedEnergy:", producedEnergy,
              "ConsumedEnergy:", consumedEnergy, "EnergyPrice:", energyPrice)

        # " EnergySurplus:  ", datapoint.EnergySurplus, " NetEnergyProduction:  ", datapoint.NetEnergyProduction)

        # fmt.Println(datapoint.Date, "Price:",calculateConsumerPrice(datapoint.ProducedEnergy, datapoint.ConsumedEnergy, datapoint.EnergyPrice,datapoint.EnergySurplus))

        datapointsForDate[date] = {"ProducedEnergy": producedEnergy, "ConsumedEnergy": consumedEnergy, "EnergyPrice": energyPrice, "EnergySurplus": energySurplus,
                                   "NetEnergyProduction": netEnergyProduction}
    return datapointsForDate


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


def getNumberOfDays(numberOfYears):
    numberOfDates = (numberOfYears * 365) + 1
    return numberOfDates


def printDataPoint(household, date):
    print("Data for " + date + ": " + str(household.DataPoints[date]))

# REST API

# Returns the current windspeed of the windmills providing electricity to the selected household, measured in m/s
def getHouseholdWindSpeed(household, date):
    windSpeedFactor = 1.375
    producedEnergy = household.DataPoints[date]["ProducedEnergy"]
    windSpeed = (producedEnergy / windSpeedFactor)
    return windSpeed

# Returns the households electricity production for a given day, measured in kWh
def getHouseholdEnergyProduction(household, date):
    producedEnergy = household.DataPoints[date]["ProducedEnergy"]
    return producedEnergy

# Returns the households electricity consumption for a given day, measured in kWh
def getHouseholdEnergyConsumption(household, date):
    consumedEnergy = household.DataPoints[date]["ConsumedEnergy"]
    return consumedEnergy

# Returns the households electricity price for a given day, measured in kr
def getHouseholdEnergyPrice(household, date):
    energyPrice = household.DataPoints[date]["EnergyPrice"]
    return energyPrice

# Returns the households electricity surplus status for a given day.
def getHouseholdEnergySurplus(household, date):
    energySurplus = household.DataPoints[date]["EnergySurplus"]
    return energySurplus

# Returns the households net energy production for a given day, measured in kWh
def getHouseholdNetEnergyProduciton(household, date):
    netEnergyProduction = household.DataPoints[date]["NetEnergyProduction"]
    return netEnergyProduction