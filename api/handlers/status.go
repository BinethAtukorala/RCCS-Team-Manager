package handlers

import (
	"fmt"
	"net/http"
)

func ProvideStatusHandler(getStatus func() string) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "GET" {

			_, _ = fmt.Fprintf(w, getStatus())
			log.Infof("Endpoint Hit: /api/status")
		} else {
			_, _ = fmt.Fprintf(w, "Invalid Method")
		}
	}
}
