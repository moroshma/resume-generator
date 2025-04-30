package resume_handlers

import (
	"bytes"
	"context"
	"encoding/json"
	"github.com/go-chi/chi/v5"
	"github.com/moroshma/resume-generator/resume_storage/internal/app/config"
	"github.com/moroshma/resume-generator/resume_storage/internal/app/middleware"
	"github.com/moroshma/resume-generator/resume_storage/internal/resume/models"
	"github.com/moroshma/resume-generator/user_service/pkg/auth_middleware"
	"github.com/sirupsen/logrus"
	"io"
	"net/http"
	"strconv"
)

type ResumeUseCase interface {
	CreateResume(ctx context.Context, userID uint, title string, resumeObject models.Resume) error
	GetResumeByID(ctx context.Context, userID, resumeID uint) (models.Resume, error)
	GetResumeInfoListByUserID(ctx context.Context, userID uint) ([]models.ResumeInfo, error)
	DeleteResumeByID(ctx context.Context, userID, resumeID uint) error
}

type ResumeHandler struct {
	resumeUseCase ResumeUseCase
}

func NewResumeHandler(resumeUseCase ResumeUseCase) *ResumeHandler {
	return &ResumeHandler{
		resumeUseCase: resumeUseCase,
	}
}

func NewResumeRoutes(r *chi.Mux, resumeUseCase ResumeUseCase, cfg *config.UserService) {
	resumeHandler := NewResumeHandler(resumeUseCase)
	r.With(middleware.AuthMiddleware(cfg.AuthService.Host)).Route("/api/v001/users", func(r chi.Router) {
		r.Post("/resume", resumeHandler.CreateResume)
		r.Delete("/resume/{id}", resumeHandler.DeleteResumeByID)
		r.Get("/resume/{id}", resumeHandler.GetResumeByID)
		r.Get("/resume/list", resumeHandler.GetResumeInfoListByUserID)
	})
}

func (h *ResumeHandler) CreateResume(w http.ResponseWriter, r *http.Request) {
	// Получаем заголовок Authorization
	authToken, err := r.Cookie("Authorization")
	if err != nil {
		http.Error(w, "Auth error: "+err.Error(), http.StatusUnauthorized)
		return
	}

	if authToken == nil || authToken.Value == "" {
		http.Error(w, "Auth error: empty token", http.StatusUnauthorized)
		return
	}

	userID, err := auth_middleware.GetUserIDByAccessToken(authToken.Value)
	if err != nil {
		http.Error(w, "Auth error: "+err.Error(), http.StatusUnauthorized)
		return
	}

	src, hdr, err := r.FormFile("resume")
	if err != nil {
		http.Error(w, "Неверный запрос: "+err.Error(), http.StatusBadRequest)
		return
	}
	defer src.Close()

	fileData, err := io.ReadAll(src)
	if err != nil {
		http.Error(w, "Ошибка чтения файла: "+err.Error(), http.StatusInternalServerError)
		return
	}

	resume := models.Resume{
		Payload:     bytes.NewReader(fileData),
		PayloadName: hdr.Filename,
		PayloadSize: hdr.Size,
	}

	err = h.resumeUseCase.CreateResume(context.Background(), userID, hdr.Filename, resume)
	if err != nil {
		logrus.Errorf("Error create resume: %v\n", err)
		http.Error(w, "Error create resume", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func (h *ResumeHandler) GetResumeByID(w http.ResponseWriter, r *http.Request) {
	authToken, err := r.Cookie("Authorization")
	if err != nil {
		http.Error(w, "Auth error: "+err.Error(), http.StatusUnauthorized)
		return
	}

	if authToken == nil || authToken.Value == "" {
		http.Error(w, "Auth error: empty token", http.StatusUnauthorized)
		return
	}

	userID, err := auth_middleware.GetUserIDByAccessToken(authToken.Value)
	if err != nil {
		http.Error(w, "Auth error: "+err.Error(), http.StatusUnauthorized)
		return
	}
	resumeIDQuery := chi.URLParam(r, "id")

	if resumeIDQuery == "" {
		http.Error(w, "ID is required", http.StatusBadRequest)
		return
	}

	resumeID, err := strconv.Atoi(resumeIDQuery)
	if err != nil {
		http.Error(w, "Invalid ID format", http.StatusBadRequest)
		return
	}

	resume, err := h.resumeUseCase.GetResumeByID(context.Background(), userID, uint(resumeID))
	if err != nil {
		logrus.Errorf("Error get resume: %v\n", err)
		http.Error(w, "Error get resume", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/pdf")

	w.Header().Set("Content-Disposition", "inline; filename="+resume.PayloadName)
	w.Header().Set("Content-Length", strconv.FormatInt(resume.PayloadSize, 10))
	if _, err := io.Copy(w, resume.Payload); err != nil {
		logrus.Errorf("Error send file to client: %v\n", err)
		http.Error(w, "Error send file to client", http.StatusInternalServerError)
		return
	}
	defer resume.Payload.(io.ReadCloser).Close()
}

func (h *ResumeHandler) GetResumeInfoListByUserID(w http.ResponseWriter, r *http.Request) {
	authToken, err := r.Cookie("Authorization")
	if err != nil {
		http.Error(w, "Auth error: "+err.Error(), http.StatusUnauthorized)
		return
	}

	if authToken == nil || authToken.Value == "" {
		http.Error(w, "Auth error: empty token", http.StatusUnauthorized)
		return
	}

	userID, err := auth_middleware.GetUserIDByAccessToken(authToken.Value)
	if err != nil {
		http.Error(w, "Auth error: "+err.Error(), http.StatusUnauthorized)
		return
	}

	resumes, err := h.resumeUseCase.GetResumeInfoListByUserID(context.Background(), userID)
	if err != nil {
		logrus.Errorf("Error get resume list: %v\n", err)
		http.Error(w, "Error get resume list", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(resumes); err != nil {
		logrus.Errorf("Error encode resume list: %v\n", err)
		http.Error(w, "Error encode resume list", http.StatusInternalServerError)
		return
	}
}

func (h *ResumeHandler) DeleteResumeByID(w http.ResponseWriter, r *http.Request) {
	authToken, err := r.Cookie("Authorization")
	if err != nil {
		http.Error(w, "Auth error: "+err.Error(), http.StatusUnauthorized)
		return
	}
	if authToken == nil || authToken.Value == "" {
		http.Error(w, "Auth error: empty token", http.StatusUnauthorized)
		return
	}
	userID, err := auth_middleware.GetUserIDByAccessToken(authToken.Value)
	if err != nil {
		http.Error(w, "Auth error: "+err.Error(), http.StatusUnauthorized)
		return
	}

	resumeIDQuery := chi.URLParam(r, "id")
	resumeID, err := strconv.Atoi(resumeIDQuery)
	if err != nil {
		http.Error(w, "Invalid ID format", http.StatusBadRequest)
		return
	}

	err = h.resumeUseCase.DeleteResumeByID(context.Background(), userID, uint(resumeID))
	if err != nil {
		logrus.Errorf("Error delete resume: %v\n", err)
		http.Error(w, "Error delete resume", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
