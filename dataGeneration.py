import datetime
import random
import math
import numpy as np
from calendar import monthrange


# Add date formatted years which accounts for leap years.
def addYears(d, years):
    try:
        # Return same day of the current year
        return d.replace(year=d.year + years)
    except ValueError:
        # If not same day, it will return other, i.e.  February 29 to March 1 etc.
        return d + (datetime.date(d.year + years, 1, 1) - datetime.date(d.year, 1, 1))


## Add a sequential date range to a list.
def createDateRange(startDate, numberOfYears):
    listOfDates = []
    i = 0

    start = startDate
    endDate = addYears(startDate, numberOfYears)  # Start Date + N Years
    # Iterate through and add each date to the list as a string.
    while start < endDate:
        test = start
        listOfDates.append(str(test.strftime("%Y-%m-%d"))) # Only 2021-01-01 not 2021-01-01 00:00:00
        start += datetime.timedelta(days=1)
    return listOfDates


# Creates and returns a list of N randomized float values within the range
def randomizeFloats(minimumFloatValue, maximumFloatValue, numberOfFloatsToRandomize):
    listOfRandomizedFloats = []

    for i in range(listOfRandomizedFloats):
        randomFloatValue = random.Random()
        print(randomFloatValue)
        listOfRandomizedFloats.append(minimumFloatValue + randomFloatValue * (maximumFloatValue - minimumFloatValue))
    return listOfRandomizedFloats


# Creates and returns a list of N randomized float values which accounts for seasonal changes.
def randomizeSeasonalFloats(startDate, days):
    listOfRandomizedFloats = []

    ## Max, Min values for each month.
    min = [20.0, 19.5, 17.0, 16.0, 14.5, 11.0, 11.0, 12.5, 14.0, 16.0, 18.5, 20.5]
    max = [24.0, 23.5, 20.0, 18.0, 16.0, 13.5, 13.5, 14.5, 15.5, 18.5, 19.5, 23.5]

    start = startDate
    for day in range(days):
        currentMonth = start.month - 1
        listOfRandomizedFloats.append(min[currentMonth] + random.random() * (max[currentMonth] - min[currentMonth]))
        start += datetime.timedelta(days=1)

    return listOfRandomizedFloats


# Creates and returns a list of float values. This is based on a sine wave inorder to receive gradual and smooth changes in the floats produced.
def generateSineWaveFloats(numberOfFloatsToRandomize):
    listOfRandomizedFloats = []

    # These ranges create a healthy range of the total NetEnergyProduction.
    A = random.randint(10, 12)  # Amplitude (Max/Min Value)
    f = round(random.uniform(0.01, 0.1), 3)  # Frequency
    B = random.randint(-15, 15)  # Phase  (Adjust for seasons)

    C = A * 1.5  # Makes sure the values are not too low and/or negative  ##Check so randomizing the afb values does it make it negative in some config

    for i in range(numberOfFloatsToRandomize):
        listOfRandomizedFloats.append((A * math.sin(2.0 * math.pi * f * np.float64(i) + B)) + C)
    return listOfRandomizedFloats


# Create a daily Energy Price based on the demand(consumed energy) and supply(produced energy)
def calculateDailyEnergyPrice(producedEnergy, consumedEnergy):
    # High Consumption & Low Producing -> Low Price
    # Low Consumption & High Producing -> High Price

    basePrice = 10.0
    maxPrice = 300.0

    # Introduce price cap to combat infinite energy prices when windmills break.
    if (producedEnergy == 0):
        dailyElectrictyPrice = maxPrice
        isSurplusStatus = isSurplus(consumedEnergy, producedEnergy)
    else:
        demandSupplyFactor = consumedEnergy / producedEnergy

        isSurplusStatus = isSurplus(consumedEnergy, producedEnergy)
        dailyElectrictyPrice = basePrice * demandSupplyFactor

        if dailyElectrictyPrice > maxPrice:
            dailyElectrictyPrice = maxPrice

    return dailyElectrictyPrice, isSurplusStatus


# Returns a boolean telling if there is an Energy Surplus (or Energy Deficit)
# If over or under baseprice.
def isSurplus(dailyEnergyConsumption, dailyEnergyProduced):
    return dailyEnergyProduced > dailyEnergyConsumption


# Returns the net energy production.
def calculateNetEnergyProduction(producedEnergy, consumedEnergy):
    calculatedNetEnergyProduction = producedEnergy - consumedEnergy
    return calculatedNetEnergyProduction
