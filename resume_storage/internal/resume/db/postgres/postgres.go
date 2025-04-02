package postgres

import (
	"context"
	"errors"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/moroshma/resume-generator/resume_storage/internal/resume/models"
)

type postgresProvider struct {
	db *pgxpool.Pool
}

func NewPostgresProvider(db *pgxpool.Pool) (*postgresProvider, error) {
	return &postgresProvider{db: db}, nil
}

func (p *postgresProvider) CreateNewResume(ctx context.Context, resume models.Resume) (uint, error) {
	var resumeID uint
	err := p.db.QueryRow(ctx,
		"insert into resume (user_id, payload_name, payload_size) values ($1, $2, $3) RETURNING resume_id;",
		resume.User.ID, resume.PayloadName, resume.PayloadSize,
	).Scan(&resumeID)
	if err != nil {
		return 0, err
	}

	return resumeID, nil
}

func (p *postgresProvider) DeleteResumeByID(ctx context.Context, resumeID uint) error {
	ct, err := p.db.Exec(ctx, "delete from resume where resume_id = $1", resumeID)
	if err != nil {
		return err
	}
	if ct.RowsAffected() == 0 {
		return errors.New("resume not found")
	}

	return nil
}

func (p *postgresProvider) GetResumeInfoByID(ctx context.Context, resumeID uint) (models.ResumeInfo, error) {
	var resume models.ResumeInfo
	err := p.db.QueryRow(ctx,
		"select resume_id, user_id, created_at, title from resume where resume_id = $1",
		resumeID,
	).Scan(&resume.ResumeID, &resume.UserID, &resume.CreatedAt, &resume.Title)
	if err != nil {
		return models.ResumeInfo{}, err
	}

	return resume, nil
}

func (p *postgresProvider) GetAllResumesPreview(ctx context.Context) ([]models.ResumeInfo, error) {
	var resumes []models.ResumeInfo
	rows, err := p.db.Query(ctx,
		"select resume_id, user_id, created_at, title from resume",
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	for rows.Next() {
		var resume models.ResumeInfo
		err := rows.Scan(&resume.ResumeID, &resume.UserID, &resume.CreatedAt, &resume.Title)
		if err != nil {
			return nil, err
		}
		resumes = append(resumes, resume)
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}

	return resumes, nil
}

/*
 CreateNewResume - Создает новую запись резюме в базе данных
 DeleteResumeByID - Удаляет резюме по ID
 GetResumeByID - Получает резюме по ID
 GetAllResumesPreview - Получает все базовые поля всех резюме
*/
