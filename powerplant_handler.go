package main

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type Powerplant struct {
	EnergyType    string `json:"energytype"`
	City string `json:"city"`
	ConstructionYear string `json:"constructionyear"`
}

var powerplants []Powerplant

func powerplantHandler(w http.ResponseWriter, r *http.Request) {

	switch r.Method {
	case "GET":

		//Convert powerplants variable into JSON format by marshaling.
		powerplantsListBytes, err := json.Marshal(powerplants)

		// Check for errors.
		if err != nil {
			fmt.Println(fmt.Errorf("Error: %v", err))
			w.WriteHeader(http.StatusInternalServerError)
			return
		}
		// Write JSON list of powerplants to response.
		w.Write(powerplantsListBytes)

	case "POST":
		// Create new Powerplant
		powerplant := Powerplant{}

		// Send as HTML form data. (Parseform parses the form values.)
		err := r.ParseForm()

		// Check for errors
		if err != nil {
			fmt.Println(fmt.Errorf("Error: %v", err))
			w.WriteHeader(http.StatusInternalServerError)
			return
		}

		// Get all data from Form row.
		powerplant.EnergyType = r.Form.Get("energytype")
		powerplant.City = r.Form.Get("city")
		powerplant.ConstructionYear = r.Form.Get("constructionyear")

		// Add the new powerplant to our list of powerplants.
		powerplants = append(powerplants, powerplant)

		// Finally, we redirect the user to the original HTMl page (located at `/assets/`), using the http libraries `Redirect` method
		http.Redirect(w, r, "/assets/", http.StatusFound)
	}


}
