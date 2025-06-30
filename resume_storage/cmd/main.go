package main

import (
	"fmt"
	"net"
)

func main() {

	//app.Run()

	ips, err := net.LookupHost("resume-storage")
	if err != nil {
		fmt.Println(err)
		return
	}

	fmt.Printf("replicas: %v\n", ips)

	addrs, err := net.InterfaceAddrs()
	if err != nil {
		fmt.Println(err)
		return
	}

	for _, addr := range addrs {
		fmt.Printf("Address: %s\n", addr.String())
		if ipNet, ok := addr.(*net.IPNet); ok && !ipNet.IP.IsLoopback() {
			if ipNet.IP.To4() != nil {
				fmt.Printf("IP: %s\n", ipNet.IP.String())
			}
		}
	}
	for {

	}
}
