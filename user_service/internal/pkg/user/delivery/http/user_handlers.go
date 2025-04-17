package http

import (
	"encoding/json"
	"errors"
	"github.com/moroshma/resume-generator/user_service/internal/app/helper"
	"github.com/moroshma/resume-generator/user_service/internal/app/middleware"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/auth/utils"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/user/repository/tarantool"
	"net/http"
	"strings"

	"github.com/go-chi/chi/v5"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/models"
)

type userHandlers struct {
	userUseCase  models.UserUseCaseI
	tokenUseCase models.TokenUsecaseI
}

func NewUserHandlers(r *chi.Mux, userUsecase models.UserUseCaseI,
	tokenUsecase models.TokenUsecaseI) {
	handlers := &userHandlers{
		userUseCase:  userUsecase,
		tokenUseCase: tokenUsecase,
	}

	r.With(middleware.AuthMiddleware(tokenUsecase)).Route("/api/v001/users", func(r chi.Router) {
		r.Get("/info", helper.Make(handlers.getInfo))
		r.Put("/info", helper.Make(handlers.updateUserInfo))
		r.Post("/info", helper.Make(handlers.createUserInfo))
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
func (handlers *userHandlers) getInfo(w http.ResponseWriter, r *http.Request) error {
	tokenCookie, err := r.Cookie(utils.AuthTokenName)
	if err != nil {
		return helper.NewAPIError(http.StatusUnauthorized, "Authorization cookie not found")
	}
	tokenString := strings.TrimPrefix(tokenCookie.Value, "Bearer ")
	id, err := middleware.GetUserIDByAccessToken(tokenString)
	if err != nil {
		return helper.NewAPIError(http.StatusUnauthorized, "Authorization cookie not found")
	}

	user, err := handlers.userUseCase.GetUserInfo(id)
	if err != nil {
		return helper.UserInfoNotFound()
	}

	res, err := json.Marshal(user)
	if err != nil {
		return err
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write(res)

	return nil
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
func (handlers *userHandlers) updateUserInfo(w http.ResponseWriter, r *http.Request) error {
	tokenCookie, err := r.Cookie(utils.AuthTokenName)
	if err != nil {
		return helper.NewAPIError(http.StatusUnauthorized, "Authorization cookie not found")
	}

	tokenString := strings.TrimPrefix(tokenCookie.Value, "Bearer ")
	id, err := middleware.GetUserIDByAccessToken(tokenString)
	if err != nil {
		return err
	}

	var user models.UserInfo
	err = json.NewDecoder(r.Body).Decode(&user)
	if err != nil {
		return helper.InvalidJson()
	}

	userInfo, err := handlers.userUseCase.UpdateUserInfo(id, user)
	if errors.Is(err, tarantool.UserInfoNotFound) {
		return helper.NewAPIError(http.StatusNotFound, tarantool.UserInfoNotFound.Error())
	}
	if err != nil {
		return err
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(userInfo)
	return nil
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
func (handlers *userHandlers) createUserInfo(w http.ResponseWriter, r *http.Request) error {
	tokenCookie, err := r.Cookie(utils.AuthTokenName)
	if err != nil {
		return helper.NewAPIError(http.StatusUnauthorized, "Authorization cookie not found")
	}
	tokenString := strings.TrimPrefix(tokenCookie.Value, "Bearer ")
	id, err := middleware.GetUserIDByAccessToken(tokenString)
	if err != nil {
		return err
	}

	var user models.UserInfo
	err = json.NewDecoder(r.Body).Decode(&user)
	if err != nil {
		return helper.InvalidJson()
	}
	user.UserID = id

	err = handlers.userUseCase.CreateUserInfo(user)
	if err != nil {
		return helper.NewAPIError(http.StatusUnprocessableEntity, err.Error())
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	return nil
}
