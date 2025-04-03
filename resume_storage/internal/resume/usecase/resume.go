package usecase

import (
	"context"
	"github.com/moroshma/resume-generator/resume_storage/internal/resume/db"
	"github.com/moroshma/resume-generator/resume_storage/internal/resume/models"
)

type ResumeUseCase struct {
	repo    db.ResumeRepositoryI
	storage models.ResumePdfStorageI
}

func NewResumeUseCase(repo db.ResumeRepositoryI, storage models.ResumePdfStorageI) *ResumeUseCase {
	return &ResumeUseCase{
		repo:    repo,
		storage: storage,
	}
}

func (r *ResumeUseCase) CreateResume(ctx context.Context, userID uint, title string, resumeObject models.Resume) error {
	resumeID, err := r.repo.CreateResume(ctx, userID, title)
	if err != nil {
		return err
	}

	err = r.storage.UploadFile(ctx, resumeObject, generateResumeObjectName(userID, resumeID))
	if err != nil {
		return err
	}

	return nil
}

func (r *ResumeUseCase) DeleteResumeByID(ctx context.Context, userID, resumeID uint) error {
	err := r.repo.DeleteResumeByID(ctx, userID, resumeID)
	if err != nil {
		return err
	}

	_, err = r.storage.DeleteFile(ctx, generateResumeObjectName(userID, resumeID))
	if err != nil {
		return err
	}

	return nil
}

func (r *ResumeUseCase) GetResumeByID(ctx context.Context, userID, resumeID uint) (models.Resume, error) {
	resumeFile, err := r.storage.DownloadFile(ctx, generateResumeObjectName(userID, resumeID))
	if err != nil {
		return models.Resume{}, err
	}

	return resumeFile, nil
}

func (r *ResumeUseCase) GetResumeInfoListByUserID(ctx context.Context, userID uint) ([]models.ResumeInfo, error) {
	resumes, err := r.repo.GetAllResumesPreview(ctx, userID)
	if err != nil {
		return nil, err
	}

	return resumes, nil
}
