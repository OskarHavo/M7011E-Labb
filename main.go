package main


// Entrypoint
func main() {
	// Create Network.
	//network := NewNetwork()

	//Create Threads.
	//go network.listenToHTTP()

	// Infinite Loop
	//select {}

	listenToHTTP()

	db := startDatabase()
	checkVersion(db)
	readAllFromDatabase(db)
	addToDatabase("Wind", "Boden", "2019", db)
	readAllFromDatabase(db)
}
