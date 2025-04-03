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

func (p *postgresProvider) DeleteResumeByID(ctx context.Context, userID, resumeID uint) error {
	rd, err := p.db.Exec(ctx,
		"delete from resume where resume_id = $1 and user_id = $2",
		resumeID, userID,
	)
	if err != nil {
		return err
	}
	if rd.RowsAffected() == 0 {
		return errors.New("resume not found")
	}

	return nil
}

func (p *postgresProvider) GetResumeInfoByID(ctx context.Context, userID, resumeID uint) (models.ResumeInfo, error) {
	var resumeInfo models.ResumeInfo
	err := p.db.QueryRow(ctx,
		"select resume_id, user_id, created_at, title from resume where resume_id = $1 and user_id = $2",
		resumeID, userID,
	).Scan(&resumeInfo.ResumeID, &resumeInfo.UserID, &resumeInfo.CreatedAt, &resumeInfo.Title)
	if err != nil {
		return models.ResumeInfo{}, err
	}

	return resumeInfo, nil
}

func (p *postgresProvider) GetAllResumesPreview(ctx context.Context, userID uint) ([]models.ResumeInfo, error) {
	var resumes []models.ResumeInfo
	rows, err := p.db.Query(ctx,
		"select resume_id, user_id, created_at, title from resume where user_id = $1",
		userID,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var resumeInfo models.ResumeInfo
		err := rows.Scan(&resumeInfo.ResumeID, &resumeInfo.UserID, &resumeInfo.CreatedAt, &resumeInfo.Title)
		if err != nil {
			return nil, err
		}
		resumes = append(resumes, resumeInfo)
	}

	return resumes, nil
}

func (p *postgresProvider) CreateResume(ctx context.Context, userID uint, title string) (uint, error) {
	var resumeID uint
	err := p.db.QueryRow(ctx,
		"insert into resume (user_id, title) values ($1, $2) returning resume_id",
		userID, title,
	).Scan(&resumeID)
	if err != nil {
		return 0, err
	}

	return resumeID, nil
}

/* resume schema
create table resume (
    resume_id serial primary key,
    user_id int not null,
    created_at timestamp default now(),
    title varchar(1024) not null
);
*/
