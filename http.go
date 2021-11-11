package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
)
// Printas ut i http://localhost:3000/

const URLprefix = "/objects/"

// Allows you to either POST (put) data and to GET (get) data from json HTTP requests.
func (network *Network) HTTPhandler(w http.ResponseWriter, r *http.Request){
	switch r.Method {
	case "POST":
		body, error := ioutil.ReadAll(r.Body) // Read Request
		defer r.Body.Close() // Always CLOSE.
		// Check for errors or if body is empty.
		if error != nil {
			http.Error(w, "ERROR", http.StatusBadRequest)
			fmt.Println("Error when POST")
		}  else{
			// Same as in Cli.go Store
			inputMessage := string(body)

			message := map[string]string{ inputMessage: string(body)} // JSON DATA FORMAT
			jsonValue,_ := json.Marshal(message)

			w.Header().Set("Location", URLprefix+inputMessage)
			w.Header().Set("Content-Type", "application/json; charset=UTF-8")
			w.WriteHeader(http.StatusCreated)	// Status 201 as detailed

			w.Write(jsonValue)
			fmt.Println("HTTP Data Written. Hash = ", inputMessage )
		}
	case "GET":
		// Checks if there is something after the prefix.  /objects/XXXXXXXXXXXXXX
		URLcomponents := strings.Split(r.URL.Path, "/")	// [ "", "objects", "hash" ]
		hashValue := URLcomponents[2]
		// Check if there is a hashvalue of correct size.
		if(len(hashValue) != 40){
			http.Error(w, "ERROR", http.StatusLengthRequired)
			fmt.Println("Error when GET ", hashValue, " is not of correct length. (40)")
		}else{
			http.Error(w, "ERROR", http.StatusLengthRequired)
		}
			// Same as in Cli.go Get
			//hash := NewKademliaID(hashValue)
			//data, nodes := network.DataLookup(hash)
		/*	data := "test"
			if data != nil {
				// If data is not nil, send OK status and write.
				w.WriteHeader(http.StatusOK)
				w.Write(data)
				fmt.Println("HTTP Data Read. Input was = ", string(data) )
			} else {
				http.Error(w, "ERROR", http.StatusNoContent)
				fmt.Println("Error when GET - DataLookUP")
			}
		} */
	default:
		http.Error(w, "Wrong. Use POST or GET", http.StatusMethodNotAllowed)
	}
}

func HelloServer(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hello, %s!", r.URL.Path[1:])
}

// Enables listening to HTTP
func (network *Network) HTTPlisten() {
	/*
	r := mux.NewRouter()
	r.HandleFunc("/objects/{hashvalue}", network.HTTPhandler).Methods("GET")
	r.HandleFunc("/objects", network.HTTPhandler).Methods("POST")
	log.Fatal(http.ListenAndServe(":3000", r))

	 */
	http.HandleFunc("/", HelloServer)
	http.ListenAndServe(":4040", nil)
}
