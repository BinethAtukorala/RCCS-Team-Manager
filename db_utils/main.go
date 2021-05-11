package db_utils

import (
	"gopkg.in/mgo.v2"
	"rccs_team_manager/models"
)

func AddTodo(todo models.TODO, database *mgo.Database) error {
	return database.C("todo").Insert(&todo)
}
