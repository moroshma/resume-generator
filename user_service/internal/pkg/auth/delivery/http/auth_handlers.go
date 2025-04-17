package http

import (
	"encoding/json"
	"errors"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/auth/utils"

	"github.com/moroshma/resume-generator/user_service/internal/app/helper"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/user/repository/tarantool"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/user/usecase"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/moroshma/resume-generator/user_service/internal/app/middleware"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/models"
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
		r.With(middleware.AuthMiddleware(tokenUseCase)).Delete("/logout", helper.Make(handlers.logOut))
		r.With(middleware.AuthMiddleware(tokenUseCase)).Get("/check", helper.Make(handlers.authCheck))
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

	utils.SetRefreshTokenCookie(w, refreshToken)
	utils.SetAccessTokenCookie(w, accessToken)

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

	utils.SetRefreshTokenCookie(w, refreshToken)

	accessToken, err := handlers.tokenUseCase.GenerateAccessTokenByUserID(authUser.ID)
	if err != nil {
		return err
	}

	utils.SetAccessTokenCookie(w, accessToken)

	w.WriteHeader(http.StatusOK)
	return nil
}

func (handlers *authHandlers) logOut(w http.ResponseWriter, _ *http.Request) error {
	utils.ClearRefreshTokenCookie(w)
	utils.ClearAccessTokenCookie(w)

	w.WriteHeader(http.StatusNoContent)
	return nil
}

func (handlers *authHandlers) generateAccessTokenByRefreshToken(w http.ResponseWriter, r *http.Request) error {
	refreshTokenCookie, err := r.Cookie(utils.RefreshTokenName)
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

	utils.SetAccessTokenCookie(w, accessToken)

	refreshToken, err = handlers.tokenUseCase.GenerateRefreshTokenByUserID(userID)
	if err != nil {
		return err
	}

	utils.SetRefreshTokenCookie(w, refreshToken)

	w.WriteHeader(http.StatusOK)
	return nil
}

func (handlers *authHandlers) authCheck(w http.ResponseWriter, _ *http.Request) error {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusNoContent)

	return nil
}
