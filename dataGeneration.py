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

# Calculates the daily power consumption. Looks at the month to produce a value based on the season,
def generateDailyPowerConsumption(date):
    min = [20.0, 19.5, 17.0, 16.0, 14.5, 11.0, 11.0, 12.5, 14.0, 16.0, 18.5, 20.5]
    max = [24.0, 23.5, 20.0, 18.0, 16.0, 13.5, 13.5, 14.5, 15.5, 18.5, 19.5, 23.5]

    currentMonth = date.month - 1  # -1 so January = [0]
    powerConsumption = (min[currentMonth] + random.random() * (max[currentMonth] - min[currentMonth]))
    return powerConsumption

# Calculates the daily power production. Based on a sinewave inorder to give a gradual increase/decrease to the harmonous wind.
# The areacode provides locational data by basing the phase of the sinewave on where you're located, and therefore houses in proximity to one another should experience similar wind patterns.
def generateDailyPowerProduction(date, startDate, areaCode):
    deltaDate = date - startDate # Calculate where in the sinewave you are.
    i = deltaDate.days

    # These ranges create a healthy range of the total NetEnergyProduction. (Kan inte randomiza för varje call, man får nog randomiza 1 gång per hus och föra in det som inparameter)
    A = 10 #random.randint(10, 12)  # Amplitude (Max/Min Value)
    f = 0.01  # Frequency
    B = areaCode # Phase  (Adjust for location)
    C = A * 1.5  # Makes sure the values are not too low and/or negative  ##Check so randomizing the afb values does it make it negative in some config

    powerProduction = A * math.sin(2.0 * math.pi * f * np.float64(i) + B) + C #Sinuswave
    #print(str(i) + " AND " + str(powerProduction ))
    return powerProduction


# Create a daily Energy Price based on the demand(consumed energy) and supply(produced energy)
# Returns the price, surplus status and netenergyproduction
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

    calculatedNetEnergyProduction = producedEnergy - consumedEnergy
    return dailyElectrictyPrice, isSurplusStatus, calculatedNetEnergyProduction


# Returns a boolean telling if there is an Energy Surplus (or Energy Deficit)
# If over or under baseprice.
def isSurplus(dailyEnergyConsumption, dailyEnergyProduced):
    return dailyEnergyProduced > dailyEnergyConsumption

# Returns an areacode which determines what location is in based on the house's id.
def generateAreaCode(houseID):

    areaCode = houseID % 10
    return areaCode