package api

import (
	"gopkg.in/mgo.v2"
	"net/http"
	"rccs_team_manager/api/handlers"
)

type Server struct {
	Addr      string
	GetStatus func() string
	DB        *mgo.Database
}

func (s *Server) Start() error {
	return s.handleRequests()
}

func (s *Server) handleRequests() error {
	http.HandleFunc("/api/status", handlers.ProvideStatusHandler(s.GetStatus))
	http.HandleFunc("/api/todo/create", handlers.ProvideCreateTodoHandler(s.DB))
	http.HandleFunc("/api/todo/get/assigned", handlers.ProvideGetAssignedTodoHandler(s.DB))

	return http.ListenAndServe(s.Addr, nil)
}
