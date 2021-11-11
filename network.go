package main

import (
	"fmt"
	"net"
	"time"
)

type Network struct {
}

func NewNetwork() Network {
	return Network{}
}

// Listen listens for incoming requests.
func (network *Network) Listen() {
	for {

		conn, err := net.ListenUDP("udp", &net.UDPAddr{
			Port: 5001,
		})

		if err == nil {
			msg := make([]byte, 1024)
			conn.SetReadDeadline(time.Now().Add(50 * time.Millisecond))
			_, _, err := conn.ReadFromUDP(msg)

			if err != nil {
				conn.Close()
			} else {
				conn.Close()
			}
		} else {
			fmt.Println("Could not read from incoming connection.", err.Error())
		}
	}
	fmt.Println("Turning off listen")
}