package main

import (
	"crypto/tls"
	"github.com/joho/godotenv"
	"github.com/op/go-logging"
	"gopkg.in/mgo.v2"
	"log"
	"net"
	"os"
	"rccs_team_manager/api"
	"strings"
)

func main() {

	// set up logging start
	var format = logging.MustStringFormatter(
		`%{color}%{time:15:04:05.000} %{shortfunc} ▶ %{level:.4s} %{id:03x}%{color:reset} %{message}`,
	)
	logging.SetFormatter(format)
	// set up logging end

	// load .env
	if err := godotenv.Load(".env"); err != nil {
		log.Fatalln("cant load .env: " + err.Error())
	}

	// db setup start
	dialInfo := &mgo.DialInfo{
		Addrs:    strings.Split(os.Getenv("rtm_db_addr"), ","),
		Username: os.Getenv("rtm_db_username"),
		Password: os.Getenv("rtm_db_password"),
	}

	dialInfo.DialServer = func(addr *mgo.ServerAddr) (net.Conn, error) {
		conn, err := tls.Dial("tcp", addr.String(), nil)
		return conn, err
	}

	session, err := mgo.DialWithInfo(dialInfo)
	if err != nil {
		panic(err)
	}

	session.SetMode(mgo.Monotonic, true)
	// db setup end

	api_server := api.Server{
		Addr: os.Getenv("rtm_addr"),
		GetStatus: func() string {
			return "{\"status\": \"OK\"}"
		},
		DB: session.DB(os.Getenv("rtm_database_name")),
	}
	log.Fatalln(api_server.Start())
}
