package main

import (
	"fmt"
	"math/rand"
	"time"
)

// For one household on one day.
type EnergyDataPoint struct {
	Date            string  `json:"date"`
	ProducedEnergy float64 `json:"producedenergy"`
	ConsumedEnergy float64 `json:"consumedenergy"`
	EnergyPrice    float64 `json:"energyprice"`
	EnergySurplus     bool `json:"energysurplus"`
	NetEnergyProduction float64 `json:"netenergyproduction"`
}

type Household struct {
	ID int `json:"id"`
	EnergyBuffer  float64 `json:"energybuffer"` // TODO
	EnergyBuyingRatio float64 `json:"energybuyingratio"` // TODO
	EnergySellingRatio float64 `json:"energysellingratio"` // TODO
	DataPoints []EnergyDataPoint `json:"datapoints"`
}

// Used for getterrs
var datapoints []EnergyDataPoint
var households []Household


func initializeModel(){

	rand.Seed(time.Now().UnixNano())
	households = createHouseHolds(1,3)

	// TODO  Fixa så att det är lite varians i datan, så inte alla får samma sinus kurva.
}
func playModel(){
	// TODO Load first date and load each households data for that date.
	// TODO Every 5seconds move to to next date
	// TODO for each date, add datapoint.NetEnergyProduction to Household.Buffer

}

// Create Household (User) with its own datapoint list.
func createHouseHolds(howManyHouseholds int, datapointsForHowManyYears int) []Household{
	numberOfYears := datapointsForHowManyYears
	numberOfHouseholds := howManyHouseholds

	newHouseholdList := make([]Household, numberOfHouseholds )

	for i := 0; i < numberOfHouseholds; i++{
		household := Household{}
		household.ID = i
		household.EnergyBuffer = 0
		household.EnergyBuyingRatio = 0.5
		household.EnergySellingRatio = 0.5
		household.DataPoints = createDataPoints(numberOfYears)

		newHouseholdList[i] = household
	}
	return newHouseholdList
}

// Generate Date Range and Energy Values and put them into a list of structs
func createDataPoints(datapointsForHowManyYears int) []EnergyDataPoint {
	numberOfYears := datapointsForHowManyYears
	numberOfDates := getNumberOfDays(numberOfYears)
	fmt.Println("dates :", numberOfDates)

	// Generate Data
	// Wind is gradual and season like -> Sine Wave.  HouseholdPower is consistent (seasonal variation might occur though) -> Randomfloats in range.
	generatedEnergyProduction := generateSineWaveFloats(10.0, 20.0, numberOfDates)
	generatedEnergyConsumption := randomizeSeasonalFloats(numberOfDates,numberOfYears)// generateNormalDistibutionFloats(numberOfDates, numberOfYears)
	//generatedDailyEnergyPrice, generatedDailySurplusStatus := generateEnergyPrice(generatedEnergyConsumption, generatedEnergyProduction)
	generatedDateRange := createDateRange(2021,01,1,numberOfYears)

	fmt.Println("Length of generatedEnergyProduction", len(generatedEnergyProduction))
	fmt.Println("Length of generatedEnergyConsumption", len(generatedEnergyConsumption))
	//fmt.Println("Length of generatedDailyEnergyPrice", len(generatedDailyEnergyPrice))
	fmt.Println("Length of generatedDateRange", len(generatedDateRange))
	//fmt.Println("Length of generatedDailySurplusStatus", len(generatedDailySurplusStatus))

	newDatapointsList := make([]EnergyDataPoint,len (generatedDateRange) )
	daysOfOutage := 0

	// Add Date and ProducedEnergy into structs and add them to the struct list.
	for i := 0; i < numberOfDates; i++{
		datapoint := EnergyDataPoint{}
		datapoint.Date = generatedDateRange[i]

		// If Windmill breaks, an outage will occur for 2-5 days.
		if daysOfOutage == 0 && isWindmillBroken(){
			daysOfOutage = generateRandomInteger(3,6)
		}

		// If Windmill broken, produced energy will plummet (Still a value so no infinite electricity price)
		// Otherwise take from datalist
		if daysOfOutage !=0{
			datapoint.ProducedEnergy = 1.000000000000001
			daysOfOutage--
		}else{
			datapoint.ProducedEnergy = generatedEnergyProduction[i]
		}
		datapoint.ConsumedEnergy = generatedEnergyConsumption[i]
		datapoint.EnergyPrice, datapoint.EnergySurplus = calculateDailyEnergyPrice(datapoint.ProducedEnergy, datapoint.ConsumedEnergy)
		datapoint.NetEnergyProduction = calculateNetEnergyProduction(datapoint.ProducedEnergy, datapoint.ConsumedEnergy)

		fmt.Println("Date: ", datapoint.Date, " ProducedEnergy:  ",datapoint.ProducedEnergy,
			" ConsumedEnergy:  ",datapoint.ConsumedEnergy , " EnergyPrice:  ",datapoint.EnergyPrice ,
		)


		//	" EnergySurplus:  ",datapoint.EnergySurplus, " NetEnergyProduction:  ",datapoint.NetEnergyProduction)

	//	fmt.Println(datapoint.Date,"Price:",calculateConsumerPrice( datapoint.ProducedEnergy ,  datapoint.ConsumedEnergy ,datapoint.EnergyPrice, datapoint.EnergySurplus))
		newDatapointsList[i] = datapoint
	}
	return newDatapointsList
}
func updateListAfterDowntime(datapoint EnergyDataPoint){
	datapoint.ProducedEnergy = 0
	datapoint.EnergySurplus = isSurplus(datapoint.ConsumedEnergy , datapoint.ProducedEnergy)
	datapoint.NetEnergyProduction = calculateNetEnergyProduction(datapoint.ProducedEnergy, datapoint.ConsumedEnergy)
}


func getNumberOfDays(numberOfYears int) int{
	numberOfDates := (numberOfYears * 365) +1
	return numberOfDates
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
// Checks if windmill is to suffer an outage.
func isWindmillBroken() bool{
	randomInteger := generateRandomInteger(1,500)

	// 1/500 Chance for Windmill to break.
	if randomInteger == 42{
		return true
	}else{
		return false
	}
}


// REST API
func getHouseholdWindSpeed(date string) float64{
	// take datapoint with date as key -> windenergy for that day as value
	// divide value with value x to get the wind speed.

	windSpeed := 1.0445
	return windSpeed
}

func getHouseholdEnergyConsumption(date string) float64{
	// take datapoint with date as key -> consumption for that day as value

	electricityConsumption := 1.0445
	return electricityConsumption
}

func getElectricityPrice(date string) float64{
	// take datapoint with date as key -> price for that day as value

	electricityPrice := 1.0445
	return electricityPrice
}