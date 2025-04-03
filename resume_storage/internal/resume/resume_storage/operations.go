package resume_storage

import (
	"context"
	"fmt"
	"github.com/minio/minio-go/v7"
	"github.com/moroshma/resume-generator/resume_storage/internal/resume/models"
)

// UploadFile - Отправляет файл в minio
func (m *MinioProvider) UploadFile(ctx context.Context, object models.Resume, objectName string) error {
	_, err := m.client.PutObject(
		ctx,
		bucketName,
		objectName,
		object.Payload,
		object.PayloadSize,
		minio.PutObjectOptions{ContentType: "application/pdf"},
	)

	return err
}

// DownloadFile - Возвращает файл из minio
func (m *MinioProvider) DownloadFile(ctx context.Context, objectName string) (models.Resume, error) {
	// Проверяем существование объекта перед его получением
	_, err := m.client.StatObject(ctx, "users-resume-pdf", objectName, minio.StatObjectOptions{})
	if err != nil {
		// Обрабатываем случай, когда объект не существует
		return models.Resume{}, fmt.Errorf("объект не найден: %w", err)
	}

	reader, err := m.client.GetObject(
		ctx,
		bucketName,
		objectName,
		minio.GetObjectOptions{},
	)
	if err != nil {
		return models.Resume{}, err
	}
	defer func() {
		if err != nil {
			reader.Close()
		}
	}()

	// Получаем информацию об объекте для дополнительных метаданных
	stat, err := reader.Stat()
	if err != nil {
		return models.Resume{}, fmt.Errorf("ошибка получения информации об объекте: %w", err)
	}

	return models.Resume{
		Payload:     reader,
		PayloadName: objectName,
		PayloadSize: stat.Size,
	}, nil
}

// DeleteFile - Удаляет файл из minio
func (m *MinioProvider) DeleteFile(ctx context.Context, objectName string) (string, error) {
	err := m.client.RemoveObject(
		ctx,
		bucketName,
		objectName,
		minio.RemoveObjectOptions{},
	)

	if err != nil {
		return "", fmt.Errorf("err delete PDF: %w", err)
	}

	return objectName, nil
}
