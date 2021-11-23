import unittest

from model import *

startDate = "2021-01-01"
formattedStartDate = datetime.datetime.strptime(startDate, '%Y-%m-%d').date()
households = initializeModel(10,  formattedStartDate)

queryDate = "2022-12-31"
formattedQueryDate = datetime.datetime.strptime(queryDate, '%Y-%m-%d').date()
testdata = getDatapoint(households[0], formattedQueryDate)

class TestModel(unittest.TestCase):

    def test_getNumberOfDays(self):
        result = getNumberOfDays(1)
        expectedResult = 366
        self.assertEqual(result, expectedResult, "Should be " + str(expectedResult))

    def test_getDatapoint(self):
        result = getDatapoint(households[0], formattedQueryDate)
        expectedResult = testdata
        self.assertEqual(result, expectedResult, "Should be " + str(expectedResult))

    def test_getHouseholdEnergyProduction(self):
        result = getHouseholdEnergyProduction(households[0], formattedQueryDate)
        expectedResult = testdata["ProducedEnergy"]
        self.assertEqual(result, expectedResult, "Should be " + str(expectedResult))

    def test_getHouseholdWindSpeed(self):
        result = getHouseholdWindSpeed(households[0], formattedQueryDate)
        expectedResult = testdata["ProducedEnergy"] / 1.375
        self.assertEqual(result, expectedResult, "Should be " + str(expectedResult))

    def test_getHouseholdEnergyConsumption(self):
        result = getHouseholdEnergyConsumption(households[0], formattedQueryDate)
        expectedResult = testdata["ConsumedEnergy"]
        self.assertEqual(result, expectedResult, "Should be " + str(expectedResult))

    def test_getHouseholdEnergyPrice(self):
        result = getHouseholdEnergyPrice(households[0], formattedQueryDate)
        expectedResult = testdata["EnergyPrice"]
        self.assertEqual(result, expectedResult, "Should be " + str(expectedResult))

    def test_getHouseholdEnergySurplus(self):
        result = getHouseholdEnergySurplus(households[0], formattedQueryDate)
        expectedResult = testdata["EnergySurplus"]
        self.assertEqual(result, expectedResult, "Should be " + str(expectedResult))

    def test_getHouseholdNetEnergyProduction(self):
        result = getHouseholdNetEnergyProduction(households[0], formattedQueryDate)
        expectedResult = testdata["NetEnergyProduction"]
        self.assertEqual(result, expectedResult, "Should be " + str(expectedResult))

    def test_getHouseholdBufferSize(self):
        result = getHouseholdEnergyBufferSize(households[0], formattedQueryDate)
        expectedResult = testdata["EnergyBuffer"]
        self.assertEqual(result, expectedResult, "Should be " + str(expectedResult))

    def test_getHouseholdFinances(self):
        result = getHouseholdFinances(households[0], formattedQueryDate)
        expectedResult = testdata["Finances"]
        self.assertEqual(result, expectedResult, "Should be " + str(expectedResult))

    def test_createHouseHolds(self):
        startDate = "2021-01-01"
        formattedStartDate = datetime.datetime.strptime(startDate, '%Y-%m-%d').date()

        ## Check that the amount of households created are as expected.
        lengthOfOutputlist = len(createHouseHolds(1,formattedStartDate))
        result = lengthOfOutputlist
        expectedResult = 1
        self.assertEqual(result, expectedResult, "Should be " + str(expectedResult))

    def test_initializeModel(self):
        startDate = "2021-01-01"
        formattedStartDate = datetime.datetime.strptime(startDate, '%Y-%m-%d').date()

        ## Check that the amount of households created are as expected.
        lengthOfOutputlist = len(initializeModel(1,formattedStartDate))
        result = lengthOfOutputlist
        expectedResult = 1
        self.assertEqual(result, expectedResult, "Should be " + str(expectedResult))

    def test_createDataPoints(self):
        startDate = "2021-01-01"
        formattedStartDate = datetime.datetime.strptime(startDate, '%Y-%m-%d').date()

        household = Household()
        household.ID = 0
        household.Finances = 10000
        household.EnergyBuffer = 0
        household.EnergyBuyingRatio = 0.2
        household.EnergySellingRatio = 0.8

        ## Check that the amount of datapoints created are as expected.
        lengthOfOutputlist = len(createDataPoints(household,formattedStartDate))
        result = lengthOfOutputlist
        expectedResult = 1461  # Depends on endDate
        self.assertEqual(result, expectedResult, "Should be " + str(expectedResult))

class TestDataGeneration(unittest.TestCase):

    def test_addYears(self):
        test = 1
        ## Robyn fix pls.

    def test_generateDailyPowerConsumption(self):
        result = generateDailyPowerConsumption(formattedQueryDate)
        # The date is in december and should thus be between these boundaries set for that month.
        expectedLowerResult = 20.5
        expectedUpperResult = 23.5
        self.assertLess(result, expectedUpperResult, "Should be less than" + str(expectedUpperResult))
        self.assertGreater(result, expectedLowerResult, "Should be greater than" + str(expectedLowerResult))

    def test_generateDailyPowerProduction(self):

        formattedTestDate = formattedStartDate + datetime.timedelta(days=100) # Go to next date

        # If the sinewave works correctly the same value should be gotten every 100 iterations
        result1 = generateDailyPowerProduction(formattedStartDate, formattedStartDate)
        result2 = generateDailyPowerProduction(formattedTestDate, formattedStartDate)
        result1 = round(result1, 2)
        result2 = round(result2, 2)

        self.assertEqual(result1, result2, "Should be equal")

    def test_calculateDailyEnergyPrice(self):
        basePrice = 10.0
        maxPrice = 300.0

        # Check that the price will be equal to the base price and the surplus false, if the netenergyproduction = 0
        producedEnergy = 10.0
        consumedEnergy = 10.0
        resultPrice,resultSurplus = calculateDailyEnergyPrice(producedEnergy, consumedEnergy)
        expectedResultPrice = basePrice
        expectedResultSurplus = False
        self.assertEqual(resultPrice, expectedResultPrice, "Should be " + str(expectedResultPrice))
        self.assertEqual(resultSurplus, expectedResultSurplus, "Should be " + str(expectedResultSurplus))

        # Check that the price will be lower than the base price and the surplus true, if the netenergyproduction > 0
        producedEnergy = 15.0
        consumedEnergy = 10.0
        resultPrice, resultSurplus = calculateDailyEnergyPrice(producedEnergy, consumedEnergy)
        expectedResultPrice = 6.666666666666666
        expectedResultSurplus = True
        self.assertEqual(resultPrice, expectedResultPrice, "Should be " + str(expectedResultPrice))
        self.assertEqual(resultSurplus, expectedResultSurplus, "Should be " + str(expectedResultSurplus))

        # Check that the price will be larger than the base price and the surplus false, if the netenergyproduction < 0
        producedEnergy = 10.0
        consumedEnergy = 15.0
        resultPrice, resultSurplus = calculateDailyEnergyPrice(producedEnergy, consumedEnergy)
        expectedResultPrice = 15.0
        expectedResultSurplus = False
        self.assertEqual(resultPrice, expectedResultPrice, "Should be " + str(expectedResultPrice))
        self.assertEqual(resultSurplus, expectedResultSurplus, "Should be " + str(expectedResultSurplus))

        # Check that the price will be equal to the max price and the surplus false, if the producedenergy = 0 (windmill broken down)
        producedEnergy = 0.0
        consumedEnergy = 25.0
        resultPrice, resultSurplus = calculateDailyEnergyPrice(producedEnergy, consumedEnergy)
        expectedResultPrice = maxPrice
        expectedResultSurplus = False
        self.assertEqual(resultPrice, expectedResultPrice, "Should be " + str(expectedResultPrice))
        self.assertEqual(resultSurplus, expectedResultSurplus, "Should be " + str(expectedResultSurplus))

    def test_isSurplus(self):

        ## If consumption < production -> Surplus = True
        consumedEnergy = 10
        producedEnergy = 15
        result = isSurplus(consumedEnergy, producedEnergy)
        expectedResult = True
        self.assertEqual(result, expectedResult, "Should be " + str(expectedResult))

        ## If consumption > production -> Surplus = False
        consumedEnergy = 15
        producedEnergy = 10
        result = isSurplus(consumedEnergy, producedEnergy)
        expectedResult = False
        self.assertEqual(result, expectedResult, "Should be " + str(expectedResult))

    def test_calculateNetEnergyProduction(self):

        ## Check Positive Net Production
        consumedEnergy = 10
        producedEnergy = 15
        result = calculateNetEnergyProduction(producedEnergy, consumedEnergy)
        expectedResult = 5.0
        self.assertEqual(result, expectedResult, "Should be " + str(expectedResult))

        ## Check Negative Net Production
        consumedEnergy = 15
        producedEnergy = 10
        result = calculateNetEnergyProduction(producedEnergy, consumedEnergy)
        expectedResult = -5.0
        self.assertEqual(result, expectedResult, "Should be " + str(expectedResult))

if __name__ == '__main__':
    unittest.main()