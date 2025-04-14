package http

import (
	"encoding/json"
	"github.com/moroshma/resume-generator/user_service/internal/app/middleware"
	"net/http"
	"strings"

	"github.com/go-chi/chi/v5"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/models"
)

type userHandlers struct {
	userUseCase models.UserUseCaseI
}

func NewUserHandlers(r *chi.Mux, userUsecase models.UserUseCaseI) {
	handlers := &userHandlers{userUsecase}

	r.With(middleware.AuthMiddleware()).Route("/api/v001/users", func(r chi.Router) {
		r.Get("/info", handlers.getInfo)
		r.Put("/info", handlers.updateUserInfo)
		r.Post("/info", handlers.createUserInfo)
	})
}

// getInfo retrieves a user by its ID.
// @Summary GetUserInfo a user by ID
// @Description Retrieve a user by its ID
// @Tags users
// @Accept json
// @Produce json
// @Param id path string true "User ID"
// @Success 200 {object} models.User "User object"
// @Failure 400 {string} string "Bad Request"
// @Failure 401 {string} string "Unauthorized"
// @Router /api/v001/users/info [get]
func (handlers *userHandlers) getInfo(w http.ResponseWriter, r *http.Request) {
	tokenCookie, err := r.Cookie("Authorization")
	if err != nil {
		http.Error(w, "Authorization cookie not found", http.StatusUnauthorized)
		return
	}
	tokenString := strings.TrimPrefix(tokenCookie.Value, "Bearer ")
	id, err := middleware.GetUserIDByAccessToken(tokenString)
	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	user, err := handlers.userUseCase.GetUserInfo(id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusNoContent)
		return
	}

	res, err := json.Marshal(user)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write(res)
}

// updateUserInfo updates an existing user by its ID.
// @Summary Update a user by ID
// @Description Update an existing user identified by its ID with the provided JSON body
// @Tags users
// @Accept json
// @Produce json
// @Param id path string true "User ID"
// @Param user body models.User true "Updated user object"
// @Success 200 {string} string "OK"
// @Failure 400 {string} string "Bad Request"
// @Failure 401 {string} string "Unauthorized"
// @Failure 500 {string} string "Internal Server Error"
// @Router /api/v001/users/info [put]
func (handlers *userHandlers) updateUserInfo(w http.ResponseWriter, r *http.Request) {
	tokenCookie, err := r.Cookie("Authorization")
	if err != nil {
		http.Error(w, "Authorization cookie not found", http.StatusUnauthorized)
		return
	}

	tokenString := strings.TrimPrefix(tokenCookie.Value, "Bearer ")
	id, err := middleware.GetUserIDByAccessToken(tokenString)
	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	var user models.UserInfo
	err = json.NewDecoder(r.Body).Decode(&user)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	userInfo, err := handlers.userUseCase.UpdateUserInfo(id, user)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(userInfo)

}

// createUserInfo creates a new user info entry.
// @Summary Create a new user info
// @Description Creates a new user info entry for the authenticated user.
// @Tags users
// @Accept json
// @Produce json
// @Param user body models.UserInfo true "User info details"
// @Success 200 {string} string "OK"
// @Failure 400 {string} string "Bad Request"
// @Failure 401 {string} string "Unauthorized"
// @Failure 500 {string} string "Internal Server Error"
// @Router /api/v001/users/info [post]
func (handlers *userHandlers) createUserInfo(w http.ResponseWriter, r *http.Request) {
	tokenCookie, err := r.Cookie("Authorization")
	if err != nil {
		http.Error(w, "Authorization cookie not found", http.StatusUnauthorized)
		return
	}
	tokenString := strings.TrimPrefix(tokenCookie.Value, "Bearer ")
	id, err := middleware.GetUserIDByAccessToken(tokenString)
	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	var user models.UserInfo
	err = json.NewDecoder(r.Body).Decode(&user)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	user.UserID = id

	err = handlers.userUseCase.CreateUserInfo(user)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
}
