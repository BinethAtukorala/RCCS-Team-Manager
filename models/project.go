package models

type Project struct {
	Title       string `bson:"_title"`
	Description string `bson:"_description"`
}
