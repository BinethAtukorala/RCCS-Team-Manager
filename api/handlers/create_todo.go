package handlers

import (
	"encoding/json"
	"fmt"
	"gopkg.in/mgo.v2"
	"net/http"
	"rccs_team_manager/db_utils"
	"rccs_team_manager/models"
)

func ProvideCreateTodoHandler(database *mgo.Database) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		var decodedTodo models.TODO

		err := json.NewDecoder(r.Body).Decode(&decodedTodo)
		if err != nil {
			fmt.Fprintf(w, "Invalid format")
			log.Infof("Invalid format: ", err)
			return
		}
		log.Infof("new todo %s:%s", decodedTodo.Title, decodedTodo.Description)
		err = db_utils.AddTodo(decodedTodo, database)
		if err != nil {
			fmt.Fprintf(w, "Database err")
			log.Infof("Database error: ", err)
			return
		}

		log.Infof("Endpoint Hit: /api/todo/create")
	}
}
