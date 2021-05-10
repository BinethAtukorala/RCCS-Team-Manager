package models

import "time"

type TODO struct {
	Title       string
	Description string
	Project     Project
	Deadline    time.Time
	Members     []Member
	SubTasks    []Task
}

func (todo *TODO) IsMemberAssigned(member Member) bool {
	for _, m := range todo.Members {
		if member.DiscordId == m.DiscordId {
			return true
		}
	}
	return false
}
