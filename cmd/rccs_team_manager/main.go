package main

import (
	"crypto/tls"
	"github.com/joho/godotenv"
	"gopkg.in/mgo.v2"
	"log"
	"net"
	"os"
	"strings"
)

func main() {

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

}
