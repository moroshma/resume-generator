package http

import (
	"encoding/json"
	"errors"
	"fmt"
	"github.com/moroshma/resume-generator/user_service/internal/app/helper"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/user/repository/tarantool"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/user/usecase"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/moroshma/resume-generator/user_service/internal/app/middleware"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/models"
)

const (
	refreshTokenName = "Refresh-Token"
	authTokenName    = "Authorization"
	cookiePath       = "/"
	refreshMaxAge    = 7 * 24 * 60 * 60 // 7 days in seconds
	accessMaxAge     = 30 * 60          // 30 minutes in seconds
)

type authHandlers struct {
	userUseCase  models.UserUseCaseI
	tokenUseCase models.TokenUsecaseI
}

func NewAuthHandlers(r *chi.Mux,
	userUseCase models.UserUseCaseI,
	tokenUseCase models.TokenUsecaseI) {
	handlers := authHandlers{userUseCase, tokenUseCase}

	r.Route("/api/v001/auth", func(r chi.Router) {
		r.Get("/refresh", helper.Make(handlers.generateAccessTokenByRefreshToken))
		r.Post("/register", helper.Make(handlers.register))
		r.Post("/login", helper.Make(handlers.logIn))
		r.With(middleware.AuthMiddleware()).Delete("/logout", helper.Make(handlers.logOut))
		r.With(middleware.AuthMiddleware()).Get("/check", helper.Make(handlers.authCheck))
	})
}

func (handlers *authHandlers) register(w http.ResponseWriter, r *http.Request) error {
	var user models.User
	err := json.NewDecoder(r.Body).Decode(&user)
	if err != nil {
		return helper.NewAPIError(http.StatusBadRequest, err.Error())
	}

	generatedID, err := handlers.userUseCase.CreateUser(user)
	if errors.Is(err, tarantool.CollisionCrateUser) {
		return helper.NewAPIError(http.StatusConflict, err.Error())
	} else if errors.Is(err, usecase.WrongLoginOrPassword) {
		return helper.NewAPIError(http.StatusBadRequest, err.Error())
	}
	if err != nil {
		return err
	}

	user.ID = generatedID

	refreshToken, err := handlers.tokenUseCase.GenerateRefreshTokenByUserID(generatedID)
	if err != nil {
		return err
	}

	accessToken, err := handlers.tokenUseCase.GenerateAccessTokenByUserID(generatedID)
	if err != nil {
		return err
	}

	setRefreshTokenCookie(w, refreshToken)
	setAccessTokenCookie(w, accessToken)

	w.WriteHeader(http.StatusCreated)
	return nil
}

func (handlers *authHandlers) logIn(w http.ResponseWriter, r *http.Request) error {
	var user models.User
	err := json.NewDecoder(r.Body).Decode(&user)
	if err != nil {
		return helper.NewAPIError(http.StatusBadRequest, err.Error())
	}

	authUser, err := handlers.userUseCase.Authenticate(user)
	if err != nil {
		return helper.InvalidCredentials()
	}

	refreshToken, err := handlers.tokenUseCase.GenerateRefreshTokenByUserID(authUser.ID)
	if err != nil {
		return err
	}

	setRefreshTokenCookie(w, refreshToken)

	accessToken, err := handlers.tokenUseCase.GenerateAccessTokenByUserID(authUser.ID)
	if err != nil {
		return err
	}

	setAccessTokenCookie(w, accessToken)

	w.WriteHeader(http.StatusOK)
	return nil
}

func (handlers *authHandlers) logOut(w http.ResponseWriter, r *http.Request) error {
	clearRefreshTokenCookie(w)
	clearAccessTokenCookie(w)

	w.WriteHeader(http.StatusNoContent)
	return nil
}

func (handlers *authHandlers) generateAccessTokenByRefreshToken(w http.ResponseWriter, r *http.Request) error {
	refreshTokenCookie, err := r.Cookie(refreshTokenName)
	if err != nil {
		return helper.NewAPIError(http.StatusUnauthorized, "Refresh token not found")
	}

	refreshToken := refreshTokenCookie.Value

	userID, err := handlers.tokenUseCase.GetUserIDByRefreshToken(refreshToken)
	if err != nil {
		return helper.NewAPIError(http.StatusUnauthorized, "Refresh token not found")
	}

	accessToken, err := handlers.tokenUseCase.GenerateAccessTokenByUserID(userID)
	if err != nil {
		return err
	}

	setAccessTokenCookie(w, accessToken)

	refreshToken, err = handlers.tokenUseCase.GenerateRefreshTokenByUserID(userID)
	if err != nil {
		return err
	}

	setRefreshTokenCookie(w, refreshToken)

	w.WriteHeader(http.StatusOK)
	return nil
}

func (handlers *authHandlers) authCheck(w http.ResponseWriter, r *http.Request) error {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusNoContent)

	return nil
}

func setRefreshTokenCookie(w http.ResponseWriter, token string) {
	http.SetCookie(w, &http.Cookie{
		Name:     refreshTokenName,
		Value:    token,
		Path:     cookiePath,
		HttpOnly: true,
		MaxAge:   refreshMaxAge,
		Secure:   false,
		SameSite: http.SameSiteStrictMode,
	})
}

func setAccessTokenCookie(w http.ResponseWriter, token string) {
	http.SetCookie(w, &http.Cookie{
		Name:     authTokenName,
		Value:    fmt.Sprintf("Bearer %s", token),
		Path:     cookiePath,
		HttpOnly: true,
		MaxAge:   accessMaxAge,
		Secure:   false,
		SameSite: http.SameSiteStrictMode,
	})
}

func clearRefreshTokenCookie(w http.ResponseWriter) {
	http.SetCookie(w, &http.Cookie{
		Name:     refreshTokenName,
		Value:    "",
		Path:     cookiePath,
		HttpOnly: true,
		MaxAge:   -1,
		Secure:   false,
		SameSite: http.SameSiteStrictMode,
	})
}

func clearAccessTokenCookie(w http.ResponseWriter) {
	http.SetCookie(w, &http.Cookie{
		Name:     authTokenName,
		Value:    "",
		Path:     cookiePath,
		HttpOnly: true,
		MaxAge:   -1,
		Secure:   false,
		SameSite: http.SameSiteStrictMode,
	})
}
