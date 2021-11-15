package main

import (
	"fmt"
	"github.com/gorilla/mux"
	"net/http"
)

func newRouter() *mux.Router{
	r := mux.NewRouter()
	r.HandleFunc("/dev", HelloServer).Methods("GET")
	return r
}

// Enables listening to HTTP
func listenToHTTP(port string) {
	r := newRouter()
	err:= http.ListenAndServe(port, r)

	if err != nil {
		panic(err.Error())
	}
}

// Test
func HelloServer(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hello World !\n This is the dev branch!!")
}
