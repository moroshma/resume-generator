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
}
