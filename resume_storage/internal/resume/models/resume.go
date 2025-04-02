package models

import (
	"io"
	"time"
)

type User struct {
	ID uint
}

type Resume struct {
	User
	Payload     io.Reader
	PayloadName string
	PayloadSize int64
}

type ResumeInfo struct {
	ResumeID  uint      `json:"resume_id"`
	UserID    uint      `json:"user_id"`
	CreatedAt time.Time `json:"created_at"`
	Title     string    `json:"title"`
}
