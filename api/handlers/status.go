package handlers

import (
	"fmt"
	"net/http"
)

func ProvideStatusHandler(getStatus func() string) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, getStatus())
		log.Infof("Endpoint Hit: /api/status")
	}
}
