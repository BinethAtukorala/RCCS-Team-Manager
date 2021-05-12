package handlers

import (
	"fmt"
	"github.com/op/go-logging"
	"net/http"
)

var log = logging.MustGetLogger("handlers")

func ProvideStatusHandler(getStatus func() string) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, getStatus())
		log.Infof("Endpoint Hit: /api/status")
	}
}
