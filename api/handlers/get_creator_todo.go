package handlers

import (
	"encoding/json"
	"fmt"
	"gopkg.in/mgo.v2"
	"net/http"
	"rccs_team_manager/db_utils"
	"rccs_team_manager/models"
)

type getCreatorTodoRequest struct {
	Creator string `bson:"discordid"`
}

func ProvideGetCreatorTodoHandler(database *mgo.Database) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		var decodedRequest getCreatorTodoRequest

		err := json.NewDecoder(r.Body).Decode(&decodedRequest)
		if err != nil {
			_, _ = fmt.Fprintf(w, "Invalid format")
			log.Infof("Invalid format: ", err)
			return
		}
		var returnTodo []models.TODO

		err = db_utils.GetTODObyCreator(decodedRequest.Creator, database).All(&returnTodo)
		if err != nil {
			_, _ = fmt.Fprintf(w, "DB error")
			log.Infof("DB error: ", err)
			return
		}

		marshaledTodos, err := json.Marshal(returnTodo)
		if err != nil {
			_, _ = fmt.Fprintf(w, "Cant marshal data")
			log.Infof("Cant marshal data: ", err)
			return
		}
		_, _ = fmt.Fprintf(w, string(marshaledTodos))
		log.Infof("Endpoint Hit: /api/todo/get/creator")
	}
}
