package main

import (
	"math"
	"math/rand"
	"time"
)

// TODO error on high years  (4+)---> listOfDates[i] = date.Format("2006-01-02")
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

// Creates and returns a list of N randomized float values within the range. This simulates Seasonal Changes.
func randomizeSeasonalFloats(numberOfFloatsToRandomize int, numberOfYears int) []float64 {
	listOfRandomizedFloats := make([]float64,numberOfFloatsToRandomize)

	// Days in each month
	january := 31
	february := 28
	march := 31
	april := 30
	may := 31
	june := 30
	july := 31
	august := 31
	september := 30
	october := 31
	november := 30
	december := 31

	dateCount := 0

	for j := 0; j < numberOfYears; j++{

		for i := dateCount ; i < january + dateCount; i++{
			minimumFloatValue := 20.0
			maximumFloatValue := 24.0
			listOfRandomizedFloats[i] = minimumFloatValue + rand.Float64() * (maximumFloatValue- minimumFloatValue)
		}
		dateCount = dateCount + january

		for i := dateCount ; i < february + dateCount; i++{
			minimumFloatValue := 19.5
			maximumFloatValue := 23.5
			listOfRandomizedFloats[i] = minimumFloatValue + rand.Float64() * (maximumFloatValue- minimumFloatValue)
		}
		dateCount = dateCount + february

		for i := dateCount ; i < march + dateCount; i++{
			minimumFloatValue := 17.0
			maximumFloatValue := 20.0
			listOfRandomizedFloats[i] = minimumFloatValue + rand.Float64() * (maximumFloatValue- minimumFloatValue)
		}
		dateCount = dateCount + march

		for i := dateCount ; i < april + dateCount; i++{
			minimumFloatValue := 16.0
			maximumFloatValue := 18.0
			listOfRandomizedFloats[i] = minimumFloatValue + rand.Float64() * (maximumFloatValue- minimumFloatValue)
		}
		dateCount = dateCount + april

		for i := dateCount ; i < may + dateCount; i++{
			minimumFloatValue := 14.5
			maximumFloatValue := 16.0
			listOfRandomizedFloats[i] = minimumFloatValue + rand.Float64() * (maximumFloatValue- minimumFloatValue)
		}
		dateCount = dateCount + may

		for i := dateCount ; i < june + dateCount; i++{
			minimumFloatValue := 11.0
			maximumFloatValue := 13.5
			listOfRandomizedFloats[i] = minimumFloatValue + rand.Float64() * (maximumFloatValue- minimumFloatValue)
		}
		dateCount = dateCount + june

		for i := dateCount ; i < july + dateCount; i++{
			minimumFloatValue := 11.0
			maximumFloatValue := 13.5
			listOfRandomizedFloats[i] = minimumFloatValue + rand.Float64() * (maximumFloatValue- minimumFloatValue)
		}
		dateCount = dateCount + july

		for i := dateCount ; i < august + dateCount; i++{
			minimumFloatValue := 12.5
			maximumFloatValue := 14.5
			listOfRandomizedFloats[i] = minimumFloatValue + rand.Float64() * (maximumFloatValue- minimumFloatValue)
		}
		dateCount = dateCount + august

		for i := dateCount ; i < september + dateCount; i++{
			minimumFloatValue := 14.5
			maximumFloatValue := 15.5
			listOfRandomizedFloats[i] = minimumFloatValue + rand.Float64() * (maximumFloatValue- minimumFloatValue)
		}
		dateCount = dateCount + september

		for i := dateCount ; i < october + dateCount; i++{
			minimumFloatValue := 16.0
			maximumFloatValue := 18.5
			listOfRandomizedFloats[i] = minimumFloatValue + rand.Float64() * (maximumFloatValue- minimumFloatValue)
		}
		dateCount = dateCount + october

		for i := dateCount ; i < november + dateCount; i++{
			minimumFloatValue := 18.5
			maximumFloatValue := 19.5
			listOfRandomizedFloats[i] = minimumFloatValue + rand.Float64() * (maximumFloatValue- minimumFloatValue)
		}
		dateCount = dateCount + november

		for i := dateCount ; i < december + dateCount; i++{
			minimumFloatValue := 20.5
			maximumFloatValue := 23.0
			listOfRandomizedFloats[i] = minimumFloatValue + rand.Float64() * (maximumFloatValue- minimumFloatValue)
		}
		dateCount = dateCount + december

		}
		listOfRandomizedFloats[dateCount] = 17.1 // Last Element (Next January)
	return listOfRandomizedFloats
}

// Get a random integer within the given range.
func generateRandomInteger(minimumIntegerValue int,maximumIntegerValue int ) int{
	randomInteger := minimumIntegerValue + rand.Intn(maximumIntegerValue-minimumIntegerValue+1)
	return randomInteger
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

/*
// Creates and returns a list of float values. This is based on a normal distribution inorder to replicate a day/night cycle in the floats produced.
func generateNormalDistibutionFloats(numberOfFloatsToRandomize int, numberOfYears int ) []float64 {


	offset := calculateStepSizeOffset(numberOfFloatsToRandomize)
	listOfRandomizedFloats := make([]float64,numberOfFloatsToRandomize+offset)
	// Between 0.0-30 (amp) kWh
	fmt.Println("OFFSET = ", offset)

	amp := 30.0// Amplitude (Top Value)
	mean := 0.0 // Mean (Middle Value)
	std := 1.0 // Standard Deviation
	variance := math.Pow(std,2)  // Variance

	i := 0

	startX, endX, stepSize := calculateNormalDistributionStep(numberOfFloatsToRandomize+offset, numberOfYears)
	fmt.Println("startX = ", startX, "endX = ", endX, "stepSize = ", stepSize)

	// TODO Fixa stepSize så den funkar för alla år, hårdkoda? switch sats

	// Calculates the points in the normal distribution
	for x := startX ; x < endX ; x=x+  stepSize{


		listOfRandomizedFloats[i] = amp * math.Exp(-1.0 * math.Pow(x - mean,2.0) / (2.0*variance))
		//fmt.Println(listOfRandomizedFloats[i])

		i=i+1
		if (i == numberOfFloatsToRandomize){
			break
		}
	}
	fmt.Println("NORMAL I = ", i)
	return listOfRandomizedFloats
}
*/

/*
// Generate a Energy Price and Surplus Status for each date.
func generateEnergyPrice(energyConsumption []float64, producedEnergy []float64) ([]float64, []bool){
	numberOfFloatsToRandomize := len (producedEnergy)
	listOfEnergyPrices := make([]float64,numberOfFloatsToRandomize)
	listOfEnergySurplusStatus := make([]bool,numberOfFloatsToRandomize)

	for i:= 0; i<numberOfFloatsToRandomize; i++{
		dailyEnergyConsumption := energyConsumption[i] * 1.0

		dailyEnergyProduced := producedEnergy[i] * 1.0

		dailyElectrictyPrice, dailySurplusStatus := calculateDailyEnergyPrice(dailyEnergyConsumption,dailyEnergyProduced)

		listOfEnergyPrices[i] = dailyElectrictyPrice
		listOfEnergySurplusStatus[i] = dailySurplusStatus
	}
	return listOfEnergyPrices, listOfEnergySurplusStatus
}

/*
// Check if the number of datapoints is odd or not. If so, make it even by adding an offset.
func calculateStepSizeOffset(numberOfFloatsToRandomize int) int  {
	if(numberOfFloatsToRandomize % 2 == 1){
		return 1
	}else{
		return 0
	}
}

// Calculates the range and step size inorder to get all values.
func calculateNormalDistributionStep(numberOfFloatsToRandomize int, numberOfYears int) (float64,float64,float64){
	startX := float64(-numberOfFloatsToRandomize*numberOfYears)/(100.0)
	endX := float64(numberOfFloatsToRandomize*numberOfYears)/(100.0)
	stepSize :=  (math.Abs(startX)+endX) / float64(numberOfFloatsToRandomize)

	//fmt.Println(startX,endX,stepSize)
	return startX, endX, stepSize
}
*/

// Create a daily Energy Price based on the demand(consumed energy) and supply(produced energy)
func calculateDailyEnergyPrice(producedEnergy float64,  consumedEnergy float64) (float64, bool){
	// High Consumption & Low Producing -> Low Price
	// Low Consumption & High Producing -> High Price

	basePrice := 10.0
	demandSupplyFactor :=  consumedEnergy / producedEnergy

	isSurplusStatus := isSurplus(consumedEnergy, producedEnergy)
	dailyElectrictyPrice := basePrice * demandSupplyFactor

	return dailyElectrictyPrice, isSurplusStatus
}

// Returns a boolean telling if there is an Energy Surplus (or Energy Deficit)
// If over or under baseprice.
func isSurplus(dailyEnergyConsumption float64, dailyEnergyProduced float64) bool{
	return dailyEnergyProduced > dailyEnergyConsumption
}

// Returns the net energy production.
func calculateNetEnergyProduction(producedEnergy float64,  consumedEnergy float64) float64{
	calculateNetEnergyProduction := producedEnergy - consumedEnergy
	return calculateNetEnergyProduction
}