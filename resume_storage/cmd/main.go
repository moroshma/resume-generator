package main

import (
	"fmt"
	"github.com/moroshma/resume-generator/resume_storage/internal/app"
	"net"
)

func main() {
	app.Run()

	ips, err := net.LookupHost("resume-storage")
	if err != nil {
		fmt.Println(err)
		return
	}

	fmt.Printf("replicas: %v\n", ips)
}
