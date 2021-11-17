package main

// Entrypoint
func main() {
	// Create Network.
	//network := NewNetwork()

	//Create Threads.
	//go network.listenToHTTP()

	// Infinite Loop
	//select {}

	//listenToHTTP(":4040")
   	db := startDatabase()
    checkVersion(db)
}
