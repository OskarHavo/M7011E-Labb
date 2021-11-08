package main

import (
	"fmt"
	"net"
	"time"
)

// Network requests:
// 3 bit (1 byte) message description:
// 000: PING
// 010: STORE
// 100: FIND_NODE
// 110: FIND_DATA
// Followed by a 20 byte ID of needed and data for STORE command
// 2 bit + 20 byte +

// Protocol for returning information:
// PING_ACK: Contains nothing

// STORE_ACK: Not needed and therefore not implemented. The local node in kademlia doesn't care if the
// 			  value is successfully stored or not

// FIND_NODE_ACK: Nodes are stored in tuples with <IP, NODE_ID> in a long list without description of how many nodes there are.
// 		We already know the size of each tuple and the size of the array -> size/tuple_bytes = number of tuples

// FIND_DATA_ACK: message type followed by one byte indicating a list of nodes or some actual data.
// 		0: Found no data. Returns <=K closest nodes
// 		1: Found data. Returns the full byte array

// Golang doesn't have enums, this the closest alternative I could find
const (
	PING byte = 0
	PING_ACK byte = 1

	STORE byte = 2

	FIND_NODE byte = 4
	FIND_NODE_ACK byte = 5

	REFRESH_DATA_TTL = 6

	FIND_DATA byte = 8
	FIND_DATA_ACK_SUCCESS byte = 9
	FIND_DATA_ACK_FAIL byte = 10
)

// Message communication constants
const MAX_PACKET_SIZE = 1024 // Maximum size of a byte array
const IP_LEN = 4 // Length of IP address in bytes
const HEADER_LEN = 1 // Length of message type indicator in bytes
const BUCKET_HEADER_LEN = 1 // Length of bucket size indicator in bytes
const TIMEOUT = 50 // Amount of time before a i/o timeout is issued in milliseconds
const KAD_PORT = "5001" // Port number used for communication between nodes

type Network struct {
	running bool
	ms_service *Message_service
}

func NewNetwork(ip *net.IP, message_service *Message_service) Network {
	// TODO Enable fake connection
	return Network{NewNode(NewContact(NewKademliaIDFromIP(ip),ip.String())), true,message_service}
}

/*
// unpackMessage handles all kademlia requests from other nodes.
func (network *Network) unpackMessage(msg []byte, connection Connection, address *net.UDPAddr) error {
	switch messageType := msg[0]; messageType {
	case PING:
		//requesterID := (*KademliaID)(msg[HEADER_LEN:HEADER_LEN+ID_LEN])

		//fmt.Println("Received a PING request from node", requesterID.String())
		reply := make([]byte, HEADER_LEN)
		reply[0] = PING_ACK

		_,err := connection.WriteToUDP(reply, address)
		if err != nil {
			fmt.Println("There was an error when replying to a PING request.", err.Error())
			return err
		}
		return err
	case FIND_NODE:
		network.sendFindNodeAck(&msg, &connection, address, FIND_NODE_ACK)
		return nil
	case FIND_DATA:
		// Message format:
		// REC:  [MSG TYPE, REQUESTER ID, HASH]
		// SEND: [MSG TYPE, REQUESTER ID, BUCKET SIZE, BUCKET:[ID, IP]]
		//   OR  [MSG TYPE, DATA]
		//fmt.Println("Received a FIND_DATA request")
		hash := (*KademliaID)(msg[HEADER_LEN+ID_LEN : HEADER_LEN+ID_LEN+ID_LEN])
		data := network.localNode.LookupData(hash)
		if data != nil {
			var reply = make([]byte, HEADER_LEN+len(data))
			reply[0] = FIND_DATA_ACK_SUCCESS
			copy(reply[HEADER_LEN:], data)
			_, err := connection.WriteToUDP(reply, address)
			if err != nil {
				fmt.Println("There was an error when replying to a FIND_DATA request.", err.Error())
			}
			return err
		} else {
			network.sendFindNodeAck(&msg, &connection, address, FIND_DATA_ACK_FAIL)
		}
		return nil
	case STORE:
		// Message format:
		// REC: [MSG TYPE, REQUESTER ID, HASH, DATA...]
		// SEND: nothing
		//requesterID := (*KademliaID)(msg[HEADER_LEN:HEADER_LEN+ID_LEN])
		hash := (*KademliaID)(msg[HEADER_LEN+ID_LEN:HEADER_LEN+ID_LEN+ID_LEN])
		data := msg[HEADER_LEN+ID_LEN+ID_LEN:MAX_PACKET_SIZE]
		//fmt.Println("Received a STORE request from node", requesterID.String())

		network.localNode.Store(data, hash)
		return nil
	case REFRESH_DATA_TTL:
		// Message format:
		// SEND: [MSG TYPE, REQUESTER ID, REFRESH HASH]
		// REC: nothing
		//requesterID := (*KademliaID)(msg[HEADER_LEN:HEADER_LEN+ID_LEN])
		hash := (*KademliaID)(msg[HEADER_LEN+ID_LEN:HEADER_LEN+ID_LEN+ID_LEN])
		//fmt.Println("Received a REFRESH request from node", requesterID.String())

		network.localNode.Refresh(hash)
		return nil
	}
	return errors.New("received unknown request")
}
*/
// Listen listens for incoming requests. Once a message is received it is directed to unpackMessage.
// Also checks if the requesting node should be added to the routing table of the local node
// (see kickTheBucket)
func (network *Network) Listen() {
	for ; network.running; {

		conn, err := network.ms_service.ListenUDP("udp", &net.UDPAddr{
			Port: 5001,
		})

		if err == nil {
			msg := make([]byte, MAX_PACKET_SIZE)
			conn.SetReadDeadline(time.Now().Add(TIMEOUT * time.Millisecond))
			_, addr, err := conn.ReadFromUDP(msg)

			if err != nil {
				conn.Close()
			} else {
				ID := (*KademliaID)(msg[HEADER_LEN : HEADER_LEN+ID_LEN])

				contact := NewContact(ID, addr.IP.To4().String())
				network.localNode.routingTable.KickTheBucket(&contact,network.Ping)

				network.unpackMessage(msg, conn, addr)
				conn.Close()
			}
		} else {
			fmt.Println("Could not read from incoming connection.", err.Error())
		}
	}
	fmt.Println("Turning off listen")
}

func (network *Network) shutdown() {
	network.running = false
}


// findNodeRPC sends a FIND_NODE request to some contact with some targetID.
// Returns the k closest nodes to the target ID and if the connection to the contact was successful or not
func (network *Network) findNodeRPC(contact *Contact, targetID *KademliaID) ([]Contact, bool) {
	hostName := contact.Address
	service := hostName + ":" + KAD_PORT
	remoteAddr, err := network.ms_service.ResolveUDPAddr("udp",service)

	conn, err := network.ms_service.DialUDP("udp", nil, remoteAddr)
	if err != nil {
		fmt.Println("Could not establish connection when sending findNodeRPC to ", contact.ID.String(),"   ", contact.Address)
		return nil,false
	} else {
		// Message format:
		// SEND: [MSG TYPE, REQUESTER ID, TARGET ID]
		// REC:  [MSG TYPE, REQUESTER ID, BUCKET SIZE, BUCKET:[ID, IP]]

		// Send FIND_NODE request
		msg := make([]byte, HEADER_LEN+ID_LEN+ID_LEN)
		msg[0] = FIND_NODE
		copy(msg[HEADER_LEN : HEADER_LEN+ID_LEN], network.localNode.routingTable.me.ID[:])
		copy(msg[HEADER_LEN+ID_LEN: HEADER_LEN+ID_LEN+ID_LEN], targetID[:])
		conn.Write(msg)

		// Read and handle reply
		reply := make([]byte, HEADER_LEN+BUCKET_HEADER_LEN+(ID_LEN+IP_LEN)*k)
		conn.SetReadDeadline(time.Now().Add(TIMEOUT * time.Millisecond))
		_,_,err := conn.ReadFromUDP(reply)

		conn.Close()

		if err != nil {
			fmt.Println("Could not read FIND_NODE_RPC from " + contact.ID.String())
			return nil,false
		}

		kClosestReply := handleBucketReply(&reply)

		network.localNode.routingTable.KickTheBucket(contact,network.Ping)
		return kClosestReply.GetContactsAndCalcDistances(targetID), true
	}
}

// findNodeRPC sends a FIND_DATA request to some contact with some targetID.
// Returns the k closest nodes to the hash OR the data that matches the hash (in the hash, data pair)
// and if the connection to the contact was successful or not. If the connection was unsuccessful,
// both data and k closest contacts are nil.
func (network *Network) findDataRPC(contact *Contact, hash *KademliaID) ([]byte, []Contact, bool) {
	hostName := contact.Address
	service := hostName + ":" + KAD_PORT
	remoteAddr, err := network.ms_service.ResolveUDPAddr("udp",service)

	conn, err := network.ms_service.DialUDP("udp", nil, remoteAddr)
	if err != nil {
		fmt.Println("Could not establish connection when sending findDataRPC to " + contact.ID.String())
		return nil, nil, false
	} else {
		//fmt.Println("Sending FIND_DATA to node ", contact.ID.String())

		msg := make([]byte, HEADER_LEN+ID_LEN+ID_LEN)
		msg[0] = FIND_DATA
		copy(msg[HEADER_LEN : HEADER_LEN+ID_LEN], network.localNode.routingTable.me.ID[:])
		copy(msg[HEADER_LEN+ID_LEN: HEADER_LEN+ID_LEN+ID_LEN], hash[:])
		conn.Write(msg)

		reply := make([]byte, MAX_PACKET_SIZE)
		conn.SetReadDeadline(time.Now().Add(TIMEOUT * time.Millisecond))
		_,_,err := conn.ReadFromUDP(reply)

		conn.Close()

		if err != nil {
			fmt.Println("Could not read FIND_DATA_RPC from " + contact.ID.String())
			return nil, nil, false
		}

		network.localNode.routingTable.KickTheBucket(contact,network.Ping)

		if reply[0] == FIND_DATA_ACK_FAIL {
			// Message format:
			// REC: [MSG TYPE, REQUESTER ID, BUCKET SIZE, BUCKET:[ID, IP]]
			// (This has the same format as findNodeAck)
			kClosestReply := handleBucketReply(&reply)
			return nil, kClosestReply.GetContactsAndCalcDistances(hash), true

		} else if reply[0] == FIND_DATA_ACK_SUCCESS {
			// Message format:
			// REC: [MSG TYPE, DATA]
			return reply[HEADER_LEN:], nil, true
		} else {
			return nil, nil, false
		}
	}
}

// storeDataRPC sends a STORE request to some contact with a hash value and some data
// The function does not care if the data is correctly stored or not by the contact
// and therefore does not return anything
func (network *Network) storeDataRPC(contact Contact, hash *KademliaID, data []byte) {
	hostName := contact.Address
	service := hostName + ":" + KAD_PORT
	remoteAddr, err := network.ms_service.ResolveUDPAddr("udp",service)
	conn, err := network.ms_service.DialUDP("udp", nil, remoteAddr)

	if err != nil {
		fmt.Println("Could not establish connection when sending storeDataRPC to " + contact.ID.String())
	} else {
		// Message format:
		// SEND: [MSG TYPE, REQUESTER ID, HASH, DATA...]
		// REC: nothing

		// Prepare STORE RPC
		storeMessage := make([]byte, HEADER_LEN+ID_LEN+ID_LEN)
		storeMessage[0] = STORE
		copy(storeMessage[HEADER_LEN:HEADER_LEN+ID_LEN], network.localNode.routingTable.me.ID[:])
		copy(storeMessage[HEADER_LEN+ID_LEN:HEADER_LEN+ID_LEN+ID_LEN], hash[:])
		storeMessage = append(storeMessage, data...)

		conn.Write(storeMessage)
	}
	conn.Close()
}
