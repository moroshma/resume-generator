package main

import (
	"encoding/json"
	"io"
	"net/http"
	"strings"

	"github.com/go-chi/chi/v5"
	"github.com/moroshma/resume-generator/resume_storage/internal/resume/models"
	"github.com/moroshma/resume-generator/resume_storage/internal/resume/resume_storage"
	"github.com/sirupsen/logrus"
)

type ResumeData struct {
	ID       string `json:"id"`
	FileName string `json:"file_name"`
	FileURL  string `json:"file_url"`
}

var resumes = make(map[string]ResumeData)

func createResumeHandler(w http.ResponseWriter, r *http.Request) {
	mp, err := resume_storage.NewMinioProvider("localhost:9000", "resume", "generator", false)
	if err != nil {
		http.Error(w, "Ошибка подключения к MinIO", http.StatusInternalServerError)
		return
	}
	if err := mp.Connect(); err != nil {
		http.Error(w, "Ошибка подключения к MinIO", http.StatusInternalServerError)
		return
	}

	src, hdr, err := r.FormFile("photo")
	if err != nil {
		http.Error(w, "Неверный запрос", http.StatusBadRequest)
		return
	}
	defer src.Close()

	img := models.Resume{
		Payload:     src,
		PayloadName: hdr.Filename,
		PayloadSize: hdr.Size,
		User: models.User{
			ID: 1,
		},
	}

	objectName, err := mp.UploadFile(r.Context(), img)
	if err != nil {
		logrus.Errorf("Ошибка загрузки файла: %v\n", err)
		http.Error(w, "Не удалось загрузить файл", http.StatusInternalServerError)
		return
	}

	resume := ResumeData{
		ID:       objectName,
		FileName: hdr.Filename,
		FileURL:  "http://localhost:8080/api/v001/user/resume/" + objectName,
	}
	resumes[objectName] = resume

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(resume)
}

func getResumeHandler(w http.ResponseWriter, r *http.Request) {
	// Получаем ID из URL
	id := chi.URLParam(r, "id")
	if id == "" {
		http.Error(w, "ID не указан", http.StatusBadRequest)
		return
	}

	mp, err := resume_storage.NewMinioProvider("localhost:9000", "resume", "generator", false)
	if err != nil {
		http.Error(w, "Ошибка подключения к MinIO", http.StatusInternalServerError)
		return
	}
	if err := mp.Connect(); err != nil {
		http.Error(w, "Ошибка подключения к MinIO", http.StatusInternalServerError)
		return
	}

	model, err := mp.DownloadFile(r.Context(), "test")
	if err != nil {
		logrus.Errorf("Ошибка скачивания файла: %v\n", err)

		// Улучшенная обработка ошибки об отсутствии файла
		if strings.Contains(err.Error(), "объект не найден") {
			http.Error(w, "Файл не найден", http.StatusNotFound)
			return
		}

		http.Error(w, "Не удалось скачать файл", http.StatusInternalServerError)
		return
	}
	defer model.Payload.(io.ReadCloser).Close()

	// Устанавливаем правильный Content-Type
	w.Header().Set("Content-Type", "application/pdf")
	w.Header().Set("Content-Disposition", "inline; filename="+model.PayloadName)

	// Копируем данные из reader в ответ
	if _, err := io.Copy(w, model.Payload); err != nil {
		logrus.Errorf("Ошибка при отправке файла клиенту: %v\n", err)
	}
}

func main() {
	r := chi.NewRouter()

	r.Post("/api/v001/user/resume", createResumeHandler)
	r.Get("/api/v001/user/resume/{id}", getResumeHandler)

	http.ListenAndServe(":8080", r)
}
