package models

import "time"

type TODO struct {
	Title       string    `bson:"_title"`
	Description string    `bson:"_description"`
	Project     string    `bson:"_project"`
	Deadline    time.Time `bson:"_deadline"`
	Members     []Member  `bson:"_members"`
	SubTasks    []Task    `bson:"_subtasks"`
	Creator     string    `bson:"_creator"`
	Done        bool      `bson:"_done"`
}

func (todo *TODO) IsMemberAssigned(member Member) bool {
	for _, m := range todo.Members {
		if member.DiscordId == m.DiscordId {
			return true
		}
	}
	return false
}
