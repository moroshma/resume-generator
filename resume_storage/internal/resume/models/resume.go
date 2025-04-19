package models

import (
	"context"
	"io"
	"time"
)

type Resume struct {
	Payload     io.Reader
	PayloadName string
	PayloadSize int64
}

type ResumeInfo struct {
	ResumeID  uint      `json:"resume_id"`
	UserID    *uint     `json:"user_id"`
	CreatedAt time.Time `json:"created_at"`
	Title     string    `json:"title"`
}

type ResumePdfStorageI interface {
	UploadFile(ctx context.Context, object Resume, objectName string) error
	DownloadFile(ctx context.Context, objectName string) (Resume, error)
	DeleteFile(ctx context.Context, objectName string) (string, error)
}
