import os.path
import unittest
import random
from dataGeneration import *
from windmill import *


class TestDataGeneration(unittest.TestCase):
    def test_PowerConsumption(self):
        random.seed(2039812)
        consumption = PowerConsumption()


        # Test one year of power production
        max = 0
        min = 9999
        for i in range(1,13):
            result = consumption.tick(datetime.date(2021,i,15))
            if result > max:
                max = result
            if result < min:
                min = result

        self.assertGreater(min,11,"Should be more than 11")
        self.assertLess(max,24,"Should be less than 24")

    def test_PowerProduction(self):
        # TODO Den här måste fixas
        return

    def test_BuyCalc(self):
        class ConsumptionProducer():
            def currentValue(self):
                return 1
        class ProductionProducer():
            def currentValue(self):
                return 10
        class PowerGrid():
            def getAvailableEnergy(self):
                return 100
        class Buffer():
            def currentValue(self):
                return 10
        calc = BuyCalc(ConsumptionProducer(),ProductionProducer(),PowerGrid(),Buffer(),1.0)

        calc.setRatio(0.5)
        self.assertEqual(calc.getRatio(),0.5, "Should be 0.5")

        quota = calc.tick()
        expected = -9
        self.assertEqual(quota,expected, "Should be " + str(expected))

    def test_SellRatioCalc(self):
        class BuyCalc():
            def currentValue(self):
                return -100

        calc = SellRatioCalc(BuyCalc(),0.5)

        sell = calc.getRatio()
        self.assertEqual(sell,0.5,"Should be 1")

        calc.setRatio(0.75)
        self.assertEqual(calc.getRatio(),0.75,"Should be 0.3")

        result = calc.tick()
        expected = 75
        self.assertEqual(result, expected, "Should be " + str(expected))

        calc.block()
        self.assertEqual(calc.getRatio(),1,"Should be 1")

        result = calc.tick()
        expected = 100
        self.assertEqual(result,expected,"Should be "+str(expected))


    def test_BufferCalc(self):
        class BuyCalc():
            def currentValue(self):
                return -100
        class SellCalc():
            def currentValue(self):
                return 75
        buffer = BufferCalc(BuyCalc(),SellCalc())
        result = buffer.tick()
        expected = 25
        self.assertEqual(result,expected, "Should be "+str(expected) )

        buffer.subtract(100)
        self.assertEqual(buffer.currentValue(),0,"Should be 0")

    def test_ConsumptionChain(self):
        class ConsumptionProducer():
            def currentValue(self):
                return 1
            def tick(self,date):
                return 1
        class ProductionProducer():
            def currentValue(self):
                return 10
            def tick(self,date):
                return 10
        class PowerGrid():
            def getAvailableEnergy(self):
                return 100
        class Buffer():
            def currentValue(self):
                return 10
            def tick(self):
                return 32
        class BuyCalc():
            def currentValue(self):
                return -100
            def tick(self):
                return -100
        class SellCalc():
            def currentValue(self):
                return 75
            def tick(self):
                return 75

        chain = ConsumptionChain(ConsumptionProducer(),ProductionProducer(),PowerGrid(),0.5,0.75)

        currentProduction, consumption, currentPurchase, powerToSell, buffer = chain.tick(datetime.date(year=2021,month=11,day=27))
        self.assertEqual(currentProduction,10,"Should be 10")
        self.assertEqual(consumption,1,"Should be 1")
        self.assertEqual(powerToSell,6.75,"Should be 6.75")
        self.assertEqual(buffer,2.25,"Should be")

    def test_RandomState(self):
        random.seed(1111)
        # Get an initial random value
        startvalue = random.random()

        # Set normal random state before we test some stuff
        random.seed(1111)

        state = RandomState(1234,[-10,10])

        # Get a random value from the state
        value = state.tick()
        warped = state.warpSample(value)

        # Has the normal random state been interrupted?
        endvalue = random.random()

        # Check the values we got
        self.assertEqual(value,0.9664535356921388,"Should be 0.96")
        self.assertEqual(warped,10.295524249534914,"Should be 10.29")

        # Check if the normal random state has been disrupted or not
        self.assertEqual(startvalue,endvalue,"Should be" + str(startvalue))

    def test_DataProducer(self):
        class CurveFunction():
            def tick(self,datetime):
                return 1
        data = DataProducer(RandomState(1234,[-100,100]),CurveFunction())
        result = data.tick(datetime.datetime(2021,12,10,10,2,9))
        self.assertEqual(result,94.29070713842776,"Should be 94.29")

    def test_lerp(self):
        self.assertEqual(lerp(0,1,0.5),0.5,"Should be 0.5")

    def test_calculateDailyEnergyPrice(self):
        basePrice = 10.0
        maxPrice = 50

        # Check that the price will be equal to the base price if the netenergyproduction = 0
        producedEnergy = 10.0
        consumedEnergy = 10.0
        resultPrice = calculateDailyEnergyPrice(producedEnergy, consumedEnergy)
        expectedResultPrice = basePrice
        expectedResultSurplus = False
        expectedResultNetProduction = 0.0
        self.assertEqual(resultPrice, expectedResultPrice, "Should be " + str(expectedResultPrice))

        # Check that the price will be lower than the base price if the netenergyproduction > 0
        producedEnergy = 15.0
        consumedEnergy = 10.0
        resultPrice = calculateDailyEnergyPrice(producedEnergy, consumedEnergy)
        expectedResultPrice = 6.666666666666666
        expectedResultSurplus = True
        expectedResultNetProduction = 5.0
        self.assertEqual(resultPrice, expectedResultPrice, "Should be " + str(expectedResultPrice))

        # Check that the price will be larger than the base price if the netenergyproduction < 0
        producedEnergy = 10.0
        consumedEnergy = 15.0
        resultPrice = calculateDailyEnergyPrice(producedEnergy, consumedEnergy)
        expectedResultPrice = 15.0
        expectedResultSurplus = False
        expectedResultNetProduction = -5.0
        self.assertEqual(resultPrice, expectedResultPrice, "Should be " + str(expectedResultPrice))

        # Check that the price will be equal to the max price if the producedenergy = 0
        producedEnergy = 0.0
        consumedEnergy = 25.0
        resultPrice = calculateDailyEnergyPrice(producedEnergy, consumedEnergy)
        expectedResultPrice = maxPrice
        expectedResultSurplus = False
        expectedResultNetProduction = -25.0
        self.assertEqual(resultPrice, expectedResultPrice, "Should be " + str(expectedResultPrice))



class TestModel(unittest.TestCase):
    class Demopower():
        def getAvailableEnergy(self):
            return 1000
        def attach(self,user):
            return
        def detach(self,user):
            return
    def test_setValue(self):
        windmill = ProductionNode("demo",97753,[-1,1],[-2,2],TestModel.Demopower())
        windmill.setValue("buyRatio",0.6)
        windmill.setValue("sellRatio",0.8)
        buy = windmill.chain.buyCalc.getRatio()
        sell = windmill.chain.sellRatio.getRatio()
        self.assertEqual(buy,0.6, "Should be 0.6")
        self.assertEqual(sell,0.8, "Should be 0.6")
        windmill.setValue("block")
        block = windmill.getBlockStatus()
        self.assertEqual(block,True, "Should be True")


if __name__ == '__main__':
    unittest.main()
