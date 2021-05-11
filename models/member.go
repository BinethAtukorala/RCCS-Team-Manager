package models

type Member struct {
	Name      string `bson:"_name"`
	DiscordId string `bson:"_discordid"`
}
