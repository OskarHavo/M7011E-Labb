package main

import (
	"fmt"
	"math/rand"
	"time"
)

type EnergyDataPoint struct {
	Date            string  `json:"date"`
	ProducedEnergy float64 `json:"producedenergy"`
	ConsumedEnergy float64 `json:"consumedenergy"`
	EnergyPrice    float64 `json:"energyprice"`
	EnergySurplus     bool `json:"energysurplus"`
}

// Used for getterrs
var datapoints []EnergyDataPoint

func initializeModel(){
	rand.Seed(time.Now().UnixNano())

	datapoints = createDataPoints(1)
}

func isBroken() bool{
	// 0.00001% chance that windmill will be broken.
	// If so, cancel that day's output and the following n days.
	// maybe done at end when in dictionary for easy changing.
	var status = false
	return status

}

// Calculate the Final Consumer Price Per Day.
func calculateConsumerPrice(producedEnergy float64,  consumedEnergy float64,energyPrice float64, isSurplus bool ) float64{

	// If surplus, no need to buy energy.
	if(isSurplus){
		consumerPrice := 0.0
		return consumerPrice

	}else{
		// Calculate the energy missing and buy it for the daily price.
		consumerPrice := (consumedEnergy-producedEnergy) * energyPrice
		return consumerPrice
	}
}


// Generate Date Range and Wind Energy Values and put them into a list of structs
func createDataPoints(datapointsForHowManyYears int) []EnergyDataPoint {
	numberOfYears := datapointsForHowManyYears
	numberOfDates := getNumberOfDays(numberOfYears)

	// Generate Data
	generatedProducedWindEnergy := generateSineWaveFloats(10.0, 20.0, numberOfDates)
	generatedHouseholdEnergyConsumption := generateNormalDistibutionFloats(30.0, numberOfDates)
	generatedDailyEnergyPrice, generatedDailySurplusStatus := generateEnergyPrice(generatedHouseholdEnergyConsumption,generatedProducedWindEnergy)
	generatedDateRange := createDateRange(2021,01,1,numberOfYears)

	fmt.Println("Length of generatedProducedWindEnergy", len(generatedProducedWindEnergy))
	fmt.Println("Length of generatedHouseholdEnergyConsumption", len(generatedHouseholdEnergyConsumption))
	fmt.Println("Length of generatedDailyEnergyPrice", len(generatedDailyEnergyPrice))
	fmt.Println("Length of generatedDateRange", len(generatedDateRange))
	fmt.Println("Length of generatedDailySurplusStatus", len(generatedDailySurplusStatus))

	newDatapointsList := make([]EnergyDataPoint,len (generatedDateRange) )

	// Add Date and ProducedEnergy into structs and add them to the struct list.
	for i := 0; i < numberOfDates; i++{
		datapoint := EnergyDataPoint{}
		datapoint.Date = generatedDateRange[i]
		datapoint.ProducedEnergy = generatedProducedWindEnergy[i]
		datapoint.ConsumedEnergy = generatedHouseholdEnergyConsumption[i]
		datapoint.EnergyPrice = generatedDailyEnergyPrice[i]
		datapoint.EnergySurplus = generatedDailySurplusStatus[i]

		fmt.Println("Date: ", datapoint.Date, " ProducedEnergy:  ",datapoint.ProducedEnergy, " ConsumedEnergy:  ",datapoint.ConsumedEnergy , " EnergyPrice:  ",datapoint.EnergyPrice , " EnergySurplus:  ",datapoint.EnergySurplus)
		fmt.Println(datapoint.Date," PRICE: ", calculateConsumerPrice(datapoint.ProducedEnergy,datapoint.ConsumedEnergy,datapoint.EnergyPrice,datapoint.EnergySurplus))
		newDatapointsList[i] = datapoint
	}
	return newDatapointsList
}

func getNumberOfDays(numberOfYears int) int{
	numberOfDates := (numberOfYears * 365) +1
	return numberOfDates
}

// REST API
func getWindSpeed(date string) float64{
	// take datapoint with date as key -> windenergy for that day as value
	// divide value with value x to get the wind speed.

	windSpeed := 1.0445
	return windSpeed
}

func getElectricityConsumption(date string) float64{
	// take datapoint with date as key -> consumption for that day as value

	electricityConsumption := 1.0445
	return electricityConsumption
}

func getElectricityPrice(date string) float64{
	// take datapoint with date as key -> price for that day as value

	electricityPrice := 1.0445
	return electricityPrice
}