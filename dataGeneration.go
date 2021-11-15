package main

import (
	"fmt"
	"math"
	"math/rand"
	"time"
)

// Create range of dates from the appointed start date until N years.
func createDateRange(year int, month time.Month, day int, numberOfYears int) []string {
	listOfDates := make([]string, getNumberOfDays(numberOfYears))
	i:= 0

	startDate := time.Date(year, month, day,0,0,0,0,time.Local)
	endDate := startDate.AddDate(numberOfYears, 0, 0) // Start Date + N Years

	// Iterate through and add each date to the list as a string.
	for date := startDate; date.After(endDate) == false; date = date.AddDate(0, 0, 1) {
		listOfDates[i] = date.Format("2006-01-02")
		i = i+1
	}
	//fmt.Println(listOfDates)
	return listOfDates
}

// Creates and returns a list of N randomized float values within the range
func randomizeFloats(minimumFloatValue float64, maximumFloatValue float64, numberOfFloatsToRandomize int) []float64 {
	listOfRandomizedFloats := make([]float64,numberOfFloatsToRandomize)

	for i := range listOfRandomizedFloats{
		randomFloatValue := rand.Float64()
		listOfRandomizedFloats[i] = minimumFloatValue + randomFloatValue * (maximumFloatValue- minimumFloatValue)
	}
	return listOfRandomizedFloats
}


// Creates and returns a list of float values. This is based on a sine wave inorder to receive gradual and smooth changes in the floats produced.
func generateSineWaveFloats(minimumFloatValue float64, maximumFloatValue float64, numberOfFloatsToRandomize int) []float64 {
	listOfRandomizedFloats := make([]float64,numberOfFloatsToRandomize)

	// Between 5-25 kWh

	A := 10.0 // Amplitude (Max/Min Value)
	f := 0.01 // Frequency
	B := 0.0  // Phase  (Adjust for seasons)

	C := A * 1.5 // Makes sure the values are not too low and/or negative

	for i := range listOfRandomizedFloats{

		listOfRandomizedFloats[i] = (A * math.Sin(2.0 * math.Pi * f * float64(i) +B) ) + C
	//	fmt.Println(listOfRandomizedFloats[i])
	}
	return listOfRandomizedFloats
}

// Creates and returns a list of float values. This is based on a normal distribution inorder to replicate a day/night cycle in the floats produced.
func generateNormalDistibutionFloats(amplitude float64, numberOfFloatsToRandomize int) []float64 {
	listOfRandomizedFloats := make([]float64,numberOfFloatsToRandomize)

	// Between 0.0-30 (amp) kWh

	amp := amplitude // Amplitude (Top Value)
	mean := 0.2 // Mean (Middle Value)
	std := 1.5 // Standard Deviation
	variance := math.Pow(std,2)  // Variance

	i := 0

	startX, endX, stepSize := calculateNormalDistributionStep(numberOfFloatsToRandomize)

	// Calculates the points in the normal distribution
	for x := startX ; x < endX ; x=x+stepSize{

		listOfRandomizedFloats[i] = amp * math.Exp(-1.0 * math.Pow(x - mean,2.0) / (2.0*variance))
		//fmt.Println(listOfRandomizedFloats[i])

		i=i+1
	}
	fmt.Println(i)
	return listOfRandomizedFloats
}

// Generate a Energy Price and Surplus Status for each date.
func generateEnergyPrice(energyConsumption []float64, producedEnergy []float64) ([]float64, []bool){
	numberOfFloatsToRandomize := len (energyConsumption)
	listOfEnergyPrices := make([]float64,numberOfFloatsToRandomize)
	listOfEnergySurplusStatus := make([]bool,numberOfFloatsToRandomize)

	for i:= 0; i<numberOfFloatsToRandomize; i++{
		dailyEnergyConsumption := energyConsumption[i] * 1.0
		dailyEnergyProduced := producedEnergy[i] * 1.0

		dailyElectrictyPrice, dailySurplusStatus := calculateDailyEnergyPrice(dailyEnergyConsumption,dailyEnergyProduced)

		listOfEnergyPrices[i] = dailyElectrictyPrice
		listOfEnergySurplusStatus[i] = dailySurplusStatus

		//fmt.Println(listOfEnergyPrices[i],listOfEnergySurplusStatus[i])
	}
	return listOfEnergyPrices, listOfEnergySurplusStatus
}

// Calculates the range and step size inorder to get all values.
func calculateNormalDistributionStep(numberOfFloatsToRandomize int) (float64,float64,float64){
	startX := float64(-numberOfFloatsToRandomize)/100.0
	endX := float64(numberOfFloatsToRandomize)/100.0
	stepSize :=  (math.Abs(startX)+endX) / float64(numberOfFloatsToRandomize)

	//fmt.Println(startX,endX,stepSize)
	return startX, endX, stepSize
}

// Create a daily Energy Price based on the demand(consumed energy) and supply(produced energy)
func calculateDailyEnergyPrice(dailyEnergyConsumption float64, dailyEnergyProduced float64) (float64, bool){
	// High Consumption & Low Producing -> Low Price
	// Low Consumption & High Producing -> High Price

	basePrice := 10.0
	demandSupplyFactor :=  dailyEnergyConsumption / dailyEnergyProduced

	isSurplusStatus := isSurplus(dailyEnergyConsumption, dailyEnergyProduced)
	dailyElectrictyPrice := basePrice * demandSupplyFactor

	return dailyElectrictyPrice, isSurplusStatus
}

// Returns a boolean telling if there is an Energy Surplus (or Energy Deficit)
// If over or under baseprice.
func isSurplus(dailyEnergyConsumption float64, dailyEnergyProduced float64) bool{
	return dailyEnergyProduced > dailyEnergyConsumption
}