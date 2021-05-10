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
