package main

import (
	"fmt"
	"net"
	"time"
)


type Network struct {
}

func NewNetwork() Network {
	// TODO Enable fake connection
	return Network{}
}


// Listen listens for incoming requests. Once a message is received it is directed to unpackMessage.
// Also checks if the requesting node should be added to the routing table of the local node
// (see kickTheBucket)
func (network *Network) Listen() {
	for {

		conn, err := net.ListenUDP("udp", &net.UDPAddr{
			Port: 5001,
		})

		if err == nil {
			msg := make([]byte, 1024)
			conn.SetReadDeadline(time.Now().Add(50 * time.Millisecond))
			_, _, err := conn.ReadFromUDP(msg)
			//_, addr, err := conn.ReadFromUDP(msg)

			if err != nil {
				conn.Close()
			} else {
				/*
				ID := (*KademliaID)(msg[HEADER_LEN : HEADER_LEN+ID_LEN])

				contact := NewContact(ID, addr.IP.To4().String())
				network.localNode.routingTable.KickTheBucket(&contact,network.Ping)

				network.unpackMessage(msg, conn, addr)
				 */
				conn.Close()

			}
		} else {
			fmt.Println("Could not read from incoming connection.", err.Error())
		}
	}
	fmt.Println("Turning off listen")
}