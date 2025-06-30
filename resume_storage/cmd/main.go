package main

import (
	"context"
	"fmt"
	"net"
	"os"

	"github.com/docker/docker/api/types"
	"github.com/docker/docker/api/types/filters"
	"github.com/docker/docker/api/types/swarm"
	"github.com/docker/docker/client"
)

func main() {
	serviceName := "resumeapp_resume-storage" // Замените на имя вашего сервиса
	networkName := "resumeapp_internal"       // Замените на имя overlay-сети

	ctx := context.Background()
	cli, err := client.NewClientWithOpts(client.FromEnv, client.WithAPIVersionNegotiation())
	if err != nil {
		panic(err)
	}

	// Получаем ID сервиса по имени
	serviceFilter := filters.NewArgs(filters.Arg("name", serviceName))
	services, err := cli.ServiceList(ctx, types.ServiceListOptions{Filters: serviceFilter})
	if err != nil || len(services) == 0 {
		fmt.Printf("Service %s not found\n", serviceName)
		os.Exit(1)
	}
	serviceID := services[0].ID

	// Получаем задачи сервиса
	taskFilter := filters.NewArgs(filters.Arg("service", serviceID))
	tasks, err := cli.TaskList(ctx, types.TaskListOptions{Filters: taskFilter})
	if err != nil {
		panic(err)
	}

	// Собираем IP-адреса
	var ips []string
	for _, task := range tasks {
		if task.Status.State != swarm.TaskStateRunning {
			continue
		}

		for _, attachment := range task.NetworksAttachments {
			if attachment.Network.Spec.Name != networkName {
				continue
			}

			for _, addr := range attachment.Addresses {
				ip, _, err := net.ParseCIDR(addr)
				if err == nil {
					ips = append(ips, ip.String())
				}
			}
		}
	}

	fmt.Printf("Service '%s' replica IPs in network '%s':\n", serviceName, networkName)
	for _, ip := range ips {
		fmt.Println("-", ip)
	}
}
