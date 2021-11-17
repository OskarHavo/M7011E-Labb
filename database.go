package main


import (
	"database/sql"
	"fmt"
	"github.com/go-sql-driver/mysql"
	"log"
	"time"

	// Using '_' we can import a driver without using it explicitly in our code.
	_ "github.com/go-sql-driver/mysql"
)

func  startDatabase() *sql.DB{

	cfg := mysql.Config{
		User:   "client",
		Passwd: "",
		Net:    "tcp",
		Addr:   "127.0.0.1:3306",
		DBName: "M7011E",
	}


	db, err := sql.Open("mysql", cfg.FormatDSN())
	db.SetConnMaxLifetime(time.Minute * 3)
	db.SetMaxOpenConns(10)
	db.SetMaxIdleConns(10)

	if err != nil {
		log.Fatalf("Could not connect to the database: %v", err)
	}

	// Ping to check if alive/reachable.
	if err := db.Ping(); err != nil {
		log.Fatalf("Unable to reach the database: %v", err)
	}
	fmt.Println("The database is reachable!")
	return db
}
func addToDatabase (energytype string, city string, constructionyear string, db *sql.DB){
	// Data we want to insert
	newPowerplant := Powerplant{
		EnergyType:       energytype,
		City:             city,
		ConstructionYear: constructionyear,
	}

	//  Insert Data
	sqlQuery := "INSERT INTO powerplants (energytype, city, constructionyear) VALUES (?, ?, ?)"
	result, err := db.Exec(sqlQuery, newPowerplant.EnergyType, newPowerplant.City,newPowerplant.ConstructionYear )

	if err != nil {
		log.Fatalf("could not insert row: %v", err)
	}

	// See how many rows were affected and print.
	rowsAffected, err := result.RowsAffected()
	if err != nil {
		log.Fatalf("Could not get affected rows: %v", err)
	}
	fmt.Println( rowsAffected, "rows were inserted into the Table")



}
func readAllFromDatabase(db *sql.DB){

	sqlQuery := "SELECT * FROM powerplants"
	res, err := db.Query(sqlQuery)

	defer res.Close()

	if err != nil {
		log.Fatal(err)
	}

	for res.Next() {

		var plant Powerplant
		err := res.Scan(&plant.ID, &plant.EnergyType, &plant.City, &plant.ConstructionYear)

		if err != nil {
			log.Fatal(err)
		}

		fmt.Printf("%v\n", plant)
	}
}

func checkVersion(db *sql.DB){
	var version string
	err2 := db.QueryRow("SELECT VERSION()").Scan(&version)

	if err2 != nil {
		log.Fatal(err2)
	}

	fmt.Println(version)

}