package models

import (
	"encoding/json"

	"github.com/golang-jwt/jwt/v5"
)

type TokenUsecaseI interface {
	GenerateRefreshTokenByUserID(uint) (string, error)
	GenerateAccessTokenByUserIDRoles(uint) (string, error)
	GetUserIDByRefreshToken(string) (uint, error)
}

type ClaimsWithRoles struct {
	jwt.RegisteredClaims
	Roles json.RawMessage `json:"roles"`
}
