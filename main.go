package main

import (
	"errors"
	"flag"
	"fmt"
	"log/slog"
	"os"
	"strings"
	"time"

	"github.com/tealok-tech/routeros/v3"
)

var (
	debug      = flag.Bool("debug", false, "debug log level mode")
	address    = flag.String("address", "192.168.88.1:8728", "Address")
	username   = flag.String("username", "admin", "Username")
	password   = flag.String("password", "admin", "Password")
	properties = flag.String("properties", "name,rx-byte,tx-byte,rx-packet,tx-packet", "Properties")
	timeout    = flag.Duration("timeout", 10*time.Second, "Connection timeout")
	interval   = flag.Duration("interval", 1*time.Second, "Interval")
)

func fatal(log *slog.Logger, message string, err error) {
	log.Error(message, slog.Any("error", err))
	os.Exit(2)
}

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

	log := slog.New(handler)

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

	for {
		var reply *routeros.Reply

		if reply, err = c.Run("/interface/print", "?disabled=false", "?running=true", "=.proplist="+*properties); err != nil {
			fatal(log, "could not run", err)
		}

		for _, re := range reply.Re {
			for _, p := range strings.Split(*properties, ",") {
				fmt.Print(re.Map[p], "\t")
			}
			fmt.Print("\n")
		}
		fmt.Print("\n")

		time.Sleep(*interval)
	}
}
