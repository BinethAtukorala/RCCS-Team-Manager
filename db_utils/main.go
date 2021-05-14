package db_utils

import (
	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"
	"rccs_team_manager/models"
)

func AddTodo(todo models.TODO, database *mgo.Database) error {
	return database.C("todo").Insert(&todo)
}

func GetAssignedTODO(member models.Member, database *mgo.Database) *mgo.Query {
	return database.C("todo").Find(bson.M{
		"_members": bson.M{
			"$elemMatch": bson.M{"_discordid": member.DiscordId},
		},
	})
}
