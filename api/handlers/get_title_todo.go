package handlers

import (
	"encoding/json"
	"fmt"
	"gopkg.in/mgo.v2"
	"net/http"
	"rccs_team_manager/db_utils"
	"rccs_team_manager/models"
)

type getTitleTodoRequest struct {
	Title string
}

func ProvideGetTitleTodoHandler(database *mgo.Database) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		var decodedRequest getTitleTodoRequest

		err := json.NewDecoder(r.Body).Decode(&decodedRequest)
		if err != nil {
			fmt.Fprintf(w, "Invalid format")
			log.Infof("Invalid format: ", err)
			return
		}
		var returnTodo []models.TODO

		err = db_utils.GetTODObyTitle(decodedRequest.Title, database).All(&returnTodo)
		if err != nil {
			fmt.Fprintf(w, "DB error")
			log.Infof("DB error: ", err)
			return
		}

		marshaledTodos, err := json.Marshal(returnTodo)
		if err != nil {
			fmt.Fprintf(w, "Cant marshal data")
			log.Infof("Cant marshal data: ", err)
			return
		}
		fmt.Fprintf(w, string(marshaledTodos))
		log.Infof("Endpoint Hit: /api/todo/get/title")
	}
}
