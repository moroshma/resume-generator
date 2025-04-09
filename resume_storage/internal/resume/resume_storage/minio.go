package resume_storage

import (
	"context"
	"fmt"
	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
	"time"
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
	for i := range 5 {
		m.client, err = minio.New(m.url, &minio.Options{
			Creds:  credentials.NewStaticV4(m.user, m.password, ""),
			Secure: m.ssl,
		})

		if err != nil && i == 4 {
			return fmt.Errorf("error connect to  MinIO: %w", err)
		}

		time.Sleep(1 * time.Second)
	}

	exists, err := m.client.BucketExists(context.Background(), bucketName)
	if err != nil {
		return fmt.Errorf("error check bucket: %w", err)
	}

	if !exists {
		err = m.client.MakeBucket(context.Background(), bucketName, minio.MakeBucketOptions{})
		if err != nil {
			return fmt.Errorf("error create bucket: %w", err)
		}
	}

	return nil
}
