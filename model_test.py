import unittest
import os

from model import *


startDate = "2021-01-01"
formattedStartDate = datetime.datetime.strptime(startDate, '%Y-%m-%d').date()
households = initializeModel(10,  formattedStartDate)

queryDate = "2022-12-31"
formattedQueryDate = datetime.datetime.strptime(queryDate, '%Y-%m-%d').date()
testdata = getDatapoint(households[0], formattedQueryDate)

class TestModel(unittest.TestCase):

    def setUp(self):
        test = 1
    def tearDown(self):
        test = 1

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

        lengthOfOutputlist = len(createHouseHolds(1,formattedStartDate))
        result = lengthOfOutputlist
        expectedResult = 1
        self.assertEqual(result, expectedResult, "Should be " + str(expectedResult))

    def test_initializeModel(self):
        startDate = "2021-01-01"
        formattedStartDate = datetime.datetime.strptime(startDate, '%Y-%m-%d').date()

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

        lengthOfOutputlist = len(createDataPoints(household,formattedStartDate))
        result = lengthOfOutputlist
        expectedResult = 1461  # Depends on endDate
        self.assertEqual(result, expectedResult, "Should be " + str(expectedResult))


if __name__ == '__main__':
    unittest.main()