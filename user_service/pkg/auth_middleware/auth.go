package auth_middleware

import (
	"strconv"
	"strings"

	"github.com/golang-jwt/jwt/v5"
)

type claimsUser struct {
	jwt.RegisteredClaims
	UserID string `json:"user_id"`
}

func GetUserIDByAccessToken(accessToken string) (uint, error) {
	accessToken = strings.TrimPrefix(accessToken, "Bearer ")

	token, _, err := jwt.NewParser().ParseUnverified(accessToken, &claimsUser{})
	if err != nil {
		return 0, err
	}

	claims := token.Claims.(*claimsUser)
	userID, err := strconv.ParseUint(claims.RegisteredClaims.Subject, 10, 64)
	return uint(userID), err
}
