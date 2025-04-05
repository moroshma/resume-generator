package usecase

import (
	"errors"
	"strconv"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/models"
)

type tokenUseCase struct{}

func NewTokenUseCase() models.TokenUsecaseI {
	return &tokenUseCase{}
}

var SECRET = []byte("private-key")

func (uc *tokenUseCase) GenerateRefreshTokenByUserID(id uint) (string, error) {
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.RegisteredClaims{
		Subject:   strconv.Itoa(int(id)),
		ExpiresAt: jwt.NewNumericDate(time.Now().Add(8760 * time.Hour)),
	})
	tokenString, err := token.SignedString(SECRET)

	return tokenString, err
}

func (uc *tokenUseCase) GenerateAccessTokenByUserID(id uint) (string, error) {
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, models.ClaimsWithRoles{
		RegisteredClaims: jwt.RegisteredClaims{
			Subject:   strconv.Itoa(int(id)),
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(8760 * time.Hour)),
		},
	})

	tokenString, err := token.SignedString(SECRET)
	return tokenString, err
}

func (uc *tokenUseCase) GetUserIDByRefreshToken(refreshToken string) (uint, error) {
	token, err := jwt.ParseWithClaims(refreshToken, &jwt.RegisteredClaims{}, func(token *jwt.Token) (interface{}, error) {
		return SECRET, nil
	})
	if err != nil {
		return 0, err
	}

	claims, ok := token.Claims.(*jwt.RegisteredClaims)
	if !ok {
		return 0, errors.New("Error parsing refresh token claims")
	}

	userID, err := strconv.ParseUint(claims.Subject, 10, 64)
	if err != nil {
		return 0, err
	}

	return uint(userID), nil
}
