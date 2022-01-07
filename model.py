import time
import json
from datetime import datetime

from python.dataGeneration import *


class Household:
    def __init__(self):
        ID = 0
        Location = 0
        Finances = 0
        DaysOfOutage = 0 ## not in dict
        EnergyBuffer = 0
        EnergyBuyingRatio = 0
        EnergySellingRatio = 0
        DataPoints = dict() # DataPoints[date] = {producedEnergy, consumedEnergy,energyPrice,energySurplus,netEnergyProduction,energyBuffer, finances}


def initializeModel(howManyHouseholds, startDate):
    random.seed(random.randint(0,100000))
    households = createHouseHolds(howManyHouseholds)

    queryDate = "2022-12-31"
    formattedQueryDate = datetime.datetime.strptime(queryDate, '%Y-%m-%d').date()
    showAllData = False
    printData = True

  #  testdata = getDatapoint(households[0], formattedQueryDate)
  #  POST(testdata)

    #####################
    playModel(startDate, households)
    #####################

    if printData:
        for household in households:
            print("\n")
            print("HOUSEHOlD: " + str(household.ID) + " at the date: " + str(formattedQueryDate))
            if(showAllData):
                print("Windspeed: " + str(getHouseholdWindSpeed(household, formattedQueryDate)) + " m/s")
                print("EnergyProduction: " + str(getHouseholdEnergyProduction(household, formattedQueryDate)) + " kWh")
                print("EnergyConsumption: " + str(getHouseholdEnergyConsumption(household, formattedQueryDate)) + " kWh")
                print("EnergyNetProduction :" + str(getHouseholdNetEnergyProduction(household, formattedQueryDate)) + " kWh")
                print("EnergyBufferSize : " + str(getHouseholdEnergyBufferSize(household, formattedQueryDate)) + " kWh")
                print("EnergySurplus is: " + str(getHouseholdEnergySurplus(household, formattedQueryDate)))
                print("EnergyPrice: " + str(getHouseholdEnergyPrice(household, formattedQueryDate)) + " kr")
                print("Finances: " + str(getHouseholdFinances(household, formattedQueryDate)) + " kr")
            else:
                print("EnergyBufferSize : " + str(getHouseholdEnergyBufferSize(household, formattedQueryDate)) + " kWh")
                print("Finances: " + str(getHouseholdFinances(household, formattedQueryDate)) + " kr")

    #printDataPoint(households[0], "2023-12-31")
    saveModel(households[0])
    return households


def playModel(startDate,households):

    date = startDate  ## Rubbes lägga till din skottår grej?
    timeBetweenDates = 15  # Seconds between while loop loops.

    # For testing
    endDate = "2025-01-01"
    formattedEndDate = datetime.datetime.strptime(endDate, '%Y-%m-%d').date()

    playMode = False  # If the 15 second simulation delay is to be applied or not.

    while True:
        start_time = time.time()  # Used for waiting between calculating data for each date. (sleeping)

        ## dubbekolla sen så denna funkar som det är tänkt.
        windmillStatus, windmillAreaCode = isWindmillBroken()

        for household in households:

            # If Windmill breaks, an outage will occur for 3-6 days.
            if household.DaysOfOutage == 0 and windmillStatus == True and household.Location == windmillAreaCode:
                household.DaysOfOutage = random.randint(3, 6)

            # If Windmill broken, produced energy will plummet (Still a value so no infinite electricity price)
            # Otherwise take calculate the produced energy.
            if household.DaysOfOutage != 0:
                producedEnergy = 0.0
                household.DaysOfOutage = household.DaysOfOutage - 1
            else:
                producedEnergy = generateDailyPowerProduction(date, startDate, household.Location)

            consumedEnergy = generateDailyPowerConsumption(date)

            energyPrice, energySurplus, netEnergyProduction = calculateDailyEnergyPrice(producedEnergy, consumedEnergy)
            household.Finances += calculateConsumerPrice(energySurplus, netEnergyProduction, energyPrice, household)

            datapoint = createDataPoint(producedEnergy, consumedEnergy, energyPrice, energySurplus, netEnergyProduction, household.EnergyBuffer, household.Finances)
            household.DataPoints[date] = datapoint

        if playMode:
            time.sleep(timeBetweenDates - (time.time() - start_time))
        date += datetime.timedelta(days=1)  # Go to next date

        if date == formattedEndDate: break



def createHouseHolds(howManyHouseholds):
    numberOfHouseholds = howManyHouseholds
    newHouseholdList = []

    for i in range(0, numberOfHouseholds):
        household = Household()
        household.ID = i
        household.Location = generateAreaCode(i)
        household.DaysOfOutage = 0
        household.Finances = 10000
        household.EnergyBuffer = 0
        household.EnergyBuyingRatio = 0.2
        household.EnergySellingRatio = 0.8
        household.DataPoints = dict()

        newHouseholdList.append(household)
    return newHouseholdList


# Calculate the Final Consumer Price Per Day.
def calculateConsumerPrice(isSurplus,netEnergyProduction,energyPrice, household):
    # If Energy Surplus: Allocate the surplus to the buffer and sell the remainder for money
    if isSurplus:
        surplus = netEnergyProduction
        household.EnergyBuffer += surplus * (1 - household.EnergySellingRatio)
        financesDelta = surplus * (household.EnergySellingRatio) * energyPrice
        return financesDelta
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
        financesDelta = -((deficit + extraDeficit) * (household.EnergyBuyingRatio) * energyPrice)
        return financesDelta

def isWindmillBroken():
    randomInteger = random.randint(1, 300)
    affectedAreaCode = random.randint(0,9)

    # 1/200 Chance for Windmill to break.
    if randomInteger == 42:
        return True, affectedAreaCode
    else:
        return False, affectedAreaCode

def getNumberOfDays(numberOfYears):
    numberOfDates = (numberOfYears * 365) + 1
    return numberOfDates


def printDataPoint(household, date):
    print("Data for " + date + ": " + str(household.DataPoints[date]))


def createDataPoint(producedEnergy, consumedEnergy, energyPrice, energySurplus, netEnergyProduction, energyBuffer, finances):
    datapoint = {"ProducedEnergy": producedEnergy, "ConsumedEnergy": consumedEnergy, "EnergyPrice": energyPrice, "EnergySurplus": energySurplus,
                                   "NetEnergyProduction": netEnergyProduction, "EnergyBuffer": energyBuffer, "Finances": finances}
    return datapoint

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

# Returns the households entire datapoint for a given day.
def getDatapoint(household, date):
    datapoint = household.DataPoints[date]
    return datapoint

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
def getHouseholdNetEnergyProduction(household, date):
    netEnergyProduction = household.DataPoints[date]["NetEnergyProduction"]
    return netEnergyProduction

# Returns the households total energybuffer size at the given day, measured in kWh
def getHouseholdEnergyBufferSize(household, date):
    energyBufferSize = household.DataPoints[date]["EnergyBuffer"]  #household.EnergyBuffer
    return energyBufferSize

# Returns the households total finances at the given day, measured in kr
def getHouseholdFinances(household, date):
    finances = household.DataPoints[date]["Finances"]  #household.Finances
    return finances


# Saves a households datapoints in a json file.
def saveModel(household):
    data = household.DataPoints
    serialized_data = {k.isoformat(): v for k, v in data.items()}
    filename = "Household_" + str(household.ID) + "_Data.json"

    with open(filename, 'w') as fp:
        json.dump(serialized_data, fp, indent=4)