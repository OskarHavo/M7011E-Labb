import random
import time
from datetime import datetime

from dataGeneration import *

class Household:
    def __init__(self):
        ID = 0
        Finances = 0
        EnergyBuffer = 0
        EnergyBuyingRatio = 0
        EnergySellingRatio = 0
        DataPoints = dict() # DataPoints[date] = {producedEnergy, consumedEnergy,energyPrice,energySurplus,netEnergyProduction,energyBuffer, finances}

households = []

def initializeModel(howManyHouseholds, datapointsForHowManyYears, startDate):
    random.seed(random.randint(0,100000))
    households = createHouseHolds(howManyHouseholds, datapointsForHowManyYears, startDate)

    queryDate = "2022-12-31"
    formattedQueryDate = datetime.datetime.strptime(queryDate, '%Y-%m-%d').date()
    showAllData = False

    for household in households:
        print("\n")
        print("HOUSEHOlD: " + str(household.ID) + " at the date: " + str(formattedQueryDate))
        if(showAllData):
            print("Windspeed: " + str(getHouseholdWindSpeed(household, formattedQueryDate)) + " m/s")
            print("EnergyProduction: " + str(getHouseholdEnergyProduction(household, formattedQueryDate)) + " kWh")
            print("EnergyConsumption: " + str(getHouseholdEnergyConsumption(household, formattedQueryDate)) + " kWh")
            print("EnergyNetProduction :" + str(getHouseholdNetEnergyProduciton(household, formattedQueryDate)) + " kWh")
            print("EnergyBufferSize : " + str(getHouseholdEnergyBufferSize(household, formattedQueryDate)) + " kWh")
            print("EnergySurplus is: " + str(getHouseholdEnergySurplus(household, formattedQueryDate)))
            print("EnergyPrice: " + str(getHouseholdEnergyPrice(household, formattedQueryDate)) + " kr")
            print("Finances: " + str(getHouseholdEnergyFinances(household, formattedQueryDate)) + " kr")
        else:
            print("EnergyBufferSize : " + str(getHouseholdEnergyBufferSize(household, formattedQueryDate)) + " kWh")
            print("Finances: " + str(getHouseholdEnergyFinances(household, formattedQueryDate)) + " kr")

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
        household.Finances = 10000
        household.EnergyBuffer = 0
        household.EnergyBuyingRatio = 0.2
        household.EnergySellingRatio = 0.8
        household.DataPoints = createDataPoints(household, numberOfYears, startDate)

        newHouseholdList.append(household)
    return newHouseholdList


def createDataPoints(household, datapointsForHowManyYears, startDate):

    datapointsForDate = dict()
    daysOfOutage = 0

    date = startDate  ## Rubbes lägga till din skottår grej?
    timeBetweenDates = 15 # Seconds between while loop loops.
    # For testing
    endDate = "2025-01-01"
    formattedEndDate = datetime.datetime.strptime(endDate, '%Y-%m-%d').date()

    while True:
        start_time = time.time() # Used for waiting between calculating data for each date. (sleeping)
        print(date)

        # If Windmill breaks, an outage will occur for 3-6 days.
        if daysOfOutage == 0 and isWindmillBroken():
            daysOfOutage = random.randint(3, 6)

        # If Windmill broken, produced energy will plummet (Still a value so no infinite electricity price)
        # Otherwise take calculate the produced energy.
        if daysOfOutage != 0:
            producedEnergy = 0.0
            daysOfOutage = daysOfOutage - 1
        else:
            producedEnergy =  generateDailyPowerProduction(date, startDate)

        consumedEnergy = generateDailyPowerConsumption(date)

        energyPrice, energySurplus = calculateDailyEnergyPrice(producedEnergy, consumedEnergy)
        netEnergyProduction = calculateNetEnergyProduction(producedEnergy, consumedEnergy)

        # If Energy Surplus: Allocate the surplus to the buffer and sell the remainder for money
        if netEnergyProduction > 0:
            surplus = netEnergyProduction
            household.EnergyBuffer += surplus * (1-household.EnergySellingRatio)
            household.Finances += surplus * (household.EnergySellingRatio) * energyPrice
        # If Energy Deficit: Use your energy buffer and buy the remaining power needed with money.
        else:
            deficit = abs(netEnergyProduction)
            extraDeficit = 0

            if household.EnergyBuffer >= deficit:
                household.EnergyBuffer -= deficit * (1 - household.EnergyBuyingRatio)
            if household.EnergyBuffer < deficit:
                # If deficit depletes buffer, buy energy to set buffer to 0.
                extraDeficit = household.EnergyBuffer
                household.EnergyBuffer = 0
            household.Finances -= (deficit+extraDeficit) * (household.EnergyBuyingRatio) * energyPrice


        datapointsForDate[date] = {"ProducedEnergy": producedEnergy, "ConsumedEnergy": consumedEnergy, "EnergyPrice": energyPrice, "EnergySurplus": energySurplus,
                                   "NetEnergyProduction": netEnergyProduction, "EnergyBuffer": household.EnergyBuffer, "Finances": household.Finances}

        time.sleep(timeBetweenDates - (time.time() - start_time))
        date += datetime.timedelta(days=1) # Go to next date

        if date == formattedEndDate: break

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

    ## Avoid division by zero.
    if producedEnergy == 0:
        windSpeed = 0
    else:
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

# Returns the households total energybuffer size at the given day, measured in kWh
def getHouseholdEnergyBufferSize(household, date):
    energyBufferSize = household.DataPoints[date]["EnergyBuffer"]  #household.EnergyBuffer
    return energyBufferSize

# Returns the households total finances at the given day, measured in kr
def getHouseholdEnergyFinances(household, date):
    finances = household.DataPoints[date]["Finances"]  #household.Finances
    return finances