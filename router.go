package main

import (
	"fmt"
	"github.com/gorilla/mux"
	"net/http"
)

func newRouter() *mux.Router{
	r := mux.NewRouter()
	r.HandleFunc("/users", HelloServer).Methods("GET")

	// Create File System
	staticFileDirectory := http.Dir("./assets/") // Points to the assets directory.
	staticFileHandler := http.StripPrefix("/assets/", http.FileServer(staticFileDirectory)) //Add to router.
	r.PathPrefix("/assets/").Handler(staticFileHandler).Methods("GET") // Does not show the entire path /assets/index.html will show as /assets/

	return r
}

// Enables listening to HTTP
func listenToHTTP() {
	r := newRouter()
	err:= http.ListenAndServe(":4040", r)

	if err != nil {
		panic(err.Error())
	}
}

// Test
func HelloServer(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hello World !")
}
