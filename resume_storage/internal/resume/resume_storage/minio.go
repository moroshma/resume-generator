package resume_storage

import (
	"context"
	"fmt"
	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
)

const bucketName = "users-resume-pdf"

type MinioProvider struct {
	minioAuthData
	client *minio.Client
}

type minioAuthData struct {
	url      string
	user     string
	password string
	token    string
	ssl      bool
}

func NewMinioProvider(minioURL string, minioUser string, minioPassword string, ssl bool) (*MinioProvider, error) {
	return &MinioProvider{
		minioAuthData: minioAuthData{
			password: minioPassword,
			url:      minioURL,
			user:     minioUser,
			ssl:      ssl,
		}}, nil
}

func (m *MinioProvider) Connect() error {
	var err error
	m.client, err = minio.New(m.url, &minio.Options{
		Creds:  credentials.NewStaticV4(m.user, m.password, ""),
		Secure: m.ssl,
	})
	if err != nil {
		return fmt.Errorf("ошибка подключения к MinIO: %w", err)
	}

	// Проверяем, существует ли бакет
	exists, err := m.client.BucketExists(context.Background(), "users-resume-pdf")
	if err != nil {
		return fmt.Errorf("ошибка проверки бакета: %w", err)
	}

	// Если бакет не существует, создаем его
	if !exists {
		err = m.client.MakeBucket(context.Background(), "users-resume-pdf", minio.MakeBucketOptions{})
		if err != nil {
			return fmt.Errorf("ошибка создания бакета: %w", err)
		}
	}

	return nil
}
