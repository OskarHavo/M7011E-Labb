package main


import (
	"fmt"
	"net"
	"os"
)

// Entrypoint
func main() {
	addrs,err := net.InterfaceAddrs()
	if err != nil {
		os.Stderr.WriteString("Oops: " + err.Error() + "\n")
		os.Exit(1)
	}
	var IP net.IP
	for _, a := range addrs {
		if ipnet, ok := a.(*net.IPNet); ok && !ipnet.IP.IsLoopback() {
			if ipnet.IP.To4() != nil {
				IP = ipnet.IP
				fmt.Println(ipnet.IP.String() + "\n")
			}
		}
	}
	network := NewNetwork()
	fmt.Println("Network IP is  " + IP.String())

	//Create Threads.
	go network.HTTPlisten()

	for {

	}
}
