package main

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestStaticFileServer(t *testing.T) {
	r := newRouter()
	testServer := httptest.NewServer(r)

	resp, err := http.Get(testServer.URL + "/assets/")
	if err != nil {
		t.Fatal(err)
	}

	// Check if statuscode is OK as expected.
	result := resp.StatusCode
	expectedResult := http.StatusOK

	if result != expectedResult{
		t.Errorf("We expect Status Code to be %v ,but we got %v", expectedResult, result)
	}

}