package http

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/moroshma/resume-generator/user_service/internal/app/middleware"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/models"
)

type authHandlers struct {
	userUsecase  models.UserUseCaseI
	tokenUsecase models.TokenUsecaseI
}

func NewAuthHandlers(r *chi.Mux,
	userUseCase models.UserUseCaseI,
	tokenUseCase models.TokenUsecaseI) {
	handlers := authHandlers{userUseCase, tokenUseCase}

	r.Get("/api/v001/token", handlers.generateAccessTokenByRefreshToken)
	r.Route("/auth", func(r chi.Router) {
		r.Post("/register", handlers.register)
		r.Post("/login", handlers.logIn)
		r.With(middleware.AuthMiddleware()).Delete("/logout", handlers.logOut)
		r.With(middleware.AuthMiddleware()).Get("/check", handlers.authCheck)
	})
}

// register handles user registration.
// @Summary Register a new user
// @Description Registers a new user in the system.
// @Tags Authentication
// @Accept  json
// @Param user body models.User true "User registration details"
// @Success 201 {object} models.User "User registered successfully"
// @Failure 400 {string} string "Bad Request"
// @Router /auth/register [post]
func (handlers *authHandlers) register(w http.ResponseWriter, r *http.Request) {
	var user models.User
	err := json.NewDecoder(r.Body).Decode(&user)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	generatedID, err := handlers.userUsecase.CreateUser(user)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	user.ID = generatedID

	w.WriteHeader(http.StatusCreated)
}

// logIn handles user login.
// @Summary User login
// @Description Authenticates a user and returns access and refresh tokens.
// @Tags Authentication
// @Accept  json
// @Param user body models.User true "User login details"
// @Success 200 {string} string "Login successful"
// @Failure 400 {string} string "Bad Request"
// @Failure 401 {string} string "Unauthorized"
// @Router /auth/login [post]
func (handlers *authHandlers) logIn(w http.ResponseWriter, r *http.Request) {
	var user models.User
	err := json.NewDecoder(r.Body).Decode(&user)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	authUser, err := handlers.userUsecase.Authenticate(user)
	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	refreshToken, err := handlers.tokenUsecase.GenerateRefreshTokenByUserID(authUser.ID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	http.SetCookie(w, &http.Cookie{
		Name:     "Refresh-Token",
		Value:    refreshToken,
		Path:     "/",
		HttpOnly: true,
	})

	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	accessToken, err := handlers.tokenUsecase.GenerateAccessTokenByUserIDRoles(authUser.ID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	http.SetCookie(w, &http.Cookie{
		Name:     "Authorization",
		Value:    fmt.Sprintf("Bearer %s", accessToken),
		Path:     "/",
		HttpOnly: true,
	})

	w.WriteHeader(http.StatusOK)
}

// logOut handles user logout.
// @Summary User logout
// @Description Logs out a user by clearing access and refresh tokens.
// @Tags Authentication
// @Success 200 {string} string "Logout successful"
// @Router /auth/logout [delete]
func (handlers *authHandlers) logOut(w http.ResponseWriter, r *http.Request) {
	http.SetCookie(w, &http.Cookie{
		Name:     "Refresh-Token",
		Value:    "",
		Path:     "/",
		HttpOnly: true,
	})

	http.SetCookie(w, &http.Cookie{
		Name:     "Authorization",
		Value:    "",
		Path:     "/",
		HttpOnly: true,
	})

	w.WriteHeader(http.StatusOK)
}

// generateAccessTokenByRefreshToken generates a new access token using the provided refresh token.
// @Summary Generate access token
// @Description Generates a new access token based on the refresh token.
// @Tags Authentication
// @Success 200 {string} string "Access token generated successfully"
// @Failure 401 {string} string "Unauthorized"
// @Router /token [get]
func (handlers *authHandlers) generateAccessTokenByRefreshToken(w http.ResponseWriter, r *http.Request) {
	refreshTokenCookie, err := r.Cookie("Refresh-Token")
	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	refreshToken := refreshTokenCookie.Value

	userID, err := handlers.tokenUsecase.GetUserIDByRefreshToken(refreshToken)
	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	accessToken, err := handlers.tokenUsecase.GenerateAccessTokenByUserIDRoles(userID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	http.SetCookie(w, &http.Cookie{
		Name:     "Authorization",
		Value:    fmt.Sprintf("Bearer %s", accessToken),
		Path:     "/",
		HttpOnly: true,
	})

	w.WriteHeader(http.StatusOK)
}

func (handlers *authHandlers) authCheck(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusNoContent)
}
