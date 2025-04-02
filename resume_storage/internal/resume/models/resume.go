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

type ResumeRepositoryI interface {
	CreateResume(resume Resume) (uint, error)
	DeleteResumeByID(resumeID uint) error
	GetResumeInfoByID(resumeID uint) (ResumeInfo, error)
	GetAllResumesPreview() ([]ResumeInfo, error)
	GetResumeByID(resumeID uint) (Resume, error)
}

type ResumeUseCaseI interface {
	CreateResume(resume Resume) (uint, error)
	DeleteResumeByID(resumeID uint) error
	GetResumeInfoByID(resumeID uint) (ResumeInfo, error)
	GetAllResumesPreview() ([]ResumeInfo, error)
	GetResumeByID(resumeID uint) (Resume, error)
}

type ResumePdfStorageI interface {
	UploadFile(object Resume) (string, error)
	DownloadFile(objectName string) (Resume, error)
	DeleteFile(userID, payloadID uint) (string, error)
}
