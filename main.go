package main

import (
	"errors"
	"flag"
	"fmt"
	"log/slog"
	"os"
	"time"

	"github.com/tealok-tech/routeros/v3"
)

var (
	debug    = flag.Bool("debug", false, "debug log level mode")
	address  = flag.String("address", "192.168.88.1:8728", "Address")
	username = flag.String("username", "admin", "Username")
	password = flag.String("password", "admin", "Password")
	timeout  = flag.Duration("timeout", 10*time.Second, "Connection timeout")
)

func main() {
	var err error
	if err = flag.CommandLine.Parse(os.Args[1:]); err != nil {
		panic(err)
	}

	logLevel := slog.LevelInfo
	if debug != nil && *debug {
		logLevel = slog.LevelDebug
	}

	handler := slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		AddSource: true,
		Level:     logLevel,
	})

	slog.New(handler)

	c, err := routeros.DialTimeout(*address, *username, *password, *timeout)
	if err != nil {
		if errors.Is(err, routeros.ErrInvalidAuthentication) {
			fmt.Println("Looks like the username or password is incorrect. Please double-check what you provided via '-username' and '-password'")
			os.Exit(1)
		} else {
			fmt.Println("Error dialing router:", err)
			os.Exit(2)
		}
	}

	c.SetLogHandler(handler)

	// Get the number of interfaces
	interfaces, err := c.InterfaceList()
	for _, i := range interfaces {
		fmt.Println(i.Name, i.TXPacket)
	}
}
