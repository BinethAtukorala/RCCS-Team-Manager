package handlers

import (
	"encoding/json"
	"fmt"
	"gopkg.in/mgo.v2"
	"net/http"
	"rccs_team_manager/db_utils"
	"rccs_team_manager/models"
)

type getAssignedTodoRequest struct {
	DiscordId string `bson:"discordid"`
}

func ProvideGetAssignedTodoHandler(database *mgo.Database) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "GET" {

			var decodedTodo getAssignedTodoRequest

			err := json.NewDecoder(r.Body).Decode(&decodedTodo)
			if err != nil {
				_, _ = fmt.Fprintf(w, "Invalid format")
				log.Infof("Invalid format: ", err)
				return
			}
			var returnTodo []models.TODO

			err = db_utils.GetAssignedTODO(models.Member{
				Name:      "",
				DiscordId: decodedTodo.DiscordId,
			}, database).All(&returnTodo)
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
			log.Infof("Endpoint Hit: /api/todo/get/assigned")
		} else {
			_, _ = fmt.Fprintf(w, "Invalid Method")
		}
	}
}
