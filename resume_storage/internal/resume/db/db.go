package db

import (
	"context"
	"github.com/moroshma/resume-generator/resume_storage/internal/resume/models"
)

type ResumeRepositoryI interface {
	CreateResume(ctx context.Context, userID uint, title string) (uint, error)
	GetAllResumesPreview(ctx context.Context, userID uint) ([]models.ResumeInfo, error)
	DeleteResumeByID(ctx context.Context, userID, resumeID uint) error
	GetResumeInfoByID(ctx context.Context, userID, resumeID uint) (models.ResumeInfo, error)
}
