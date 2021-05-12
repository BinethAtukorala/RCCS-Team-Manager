package api

import (
	"net/http"
	"rccs_team_manager/api/handlers"
)

type Server struct {
	Addr      string
	GetStatus func() string
}

func (s *Server) Start() error {
	return s.handleRequests()
}

func (s *Server) handleRequests() error {
	http.HandleFunc("/api/status", handlers.ProvideStatusHandler(s.GetStatus))
	return http.ListenAndServe(s.Addr, nil)
}
