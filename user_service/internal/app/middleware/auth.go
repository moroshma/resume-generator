package middleware

import (
	"errors"
	"fmt"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/auth/utils"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/models"
	"log/slog"
	"net/http"

	"strconv"
	"strings"

	"github.com/golang-jwt/jwt/v5"
)

type claims struct {
	jwt.RegisteredClaims
}

var SECRET = []byte("private-key")

func AuthMiddleware(tokenUseCase models.TokenUsecaseI) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			refreshToken, err := r.Cookie("Refresh-Token")
			if err != nil {
				http.Error(w, fmt.Sprintf("Unauthorized Refresh-Token error:%v", err), http.StatusUnauthorized)
				return
			}

			_, err = jwt.ParseWithClaims(refreshToken.Value, &jwt.RegisteredClaims{}, func(token *jwt.Token) (interface{}, error) {
				return SECRET, nil
			})

			if err != nil {
				utils.ClearAccessTokenCookie(w)
				utils.ClearRefreshTokenCookie(w)
				http.Error(w, "Unauthorized", http.StatusUnauthorized)
				return
			}

			_, err = r.Cookie(utils.AuthTokenName)
			if errors.Is(err, http.ErrNoCookie) {
				userID, err := tokenUseCase.GetUserIDByRefreshToken(refreshToken.Value)
				if err != nil {
					utils.ClearAccessTokenCookie(w)
					utils.ClearRefreshTokenCookie(w)
					http.Error(w, "Unauthorized: Invalid refresh token", http.StatusUnauthorized)
					return
				}
				tokenString, err := tokenUseCase.GenerateAccessTokenByUserID(userID)
				if err != nil {
					http.Error(w, "Unauthorized: Failed to generate access token", http.StatusUnauthorized)
					return
				}
				utils.SetAccessTokenCookie(w, tokenString)

				newRefreshToken, tokenErr := tokenUseCase.GenerateRefreshTokenByUserID(userID)
				if tokenErr != nil {
					http.Error(w, "Internal Server Error: Could not refresh session fully", http.StatusInternalServerError)
					return
				}

				utils.SetRefreshTokenCookie(w, newRefreshToken)
			}

			next.ServeHTTP(w, r)
		})
	}
}

func GetUserIDByAccessToken(accessToken string) (uint, error) {
	accessToken = strings.TrimPrefix(accessToken, "Bearer ")
	slog.Any("-----------AccessToken:  ", accessToken)
	token, err := jwt.ParseWithClaims(accessToken, &claims{}, func(token *jwt.Token) (interface{}, error) {
		return SECRET, nil
	})
	if err != nil {
		return 0, err
	}

	claims := token.Claims.(*claims)
	userID, err := strconv.ParseUint(claims.RegisteredClaims.Subject, 10, 64)
	return uint(userID), err
}
