package middleware

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"strconv"
	"strings"

	"github.com/golang-jwt/jwt/v5"
)

type claimsWithRoles struct {
	jwt.RegisteredClaims
	Roles json.RawMessage `json:"roles"`
}

var SECRET = []byte("private-key")

var client http.Client

func findCookieByName(cookies []*http.Cookie, name string) *http.Cookie {
	for _, cookie := range cookies {
		if cookie.Name == name {
			return cookie
		}
	}
	return nil
}

func getAccessTokenByRefreshToken(refreshToken string) (string, error) {
	req, err := http.NewRequest("GET", "http://gateway/token", nil)
	if err != nil {
		return "", err
	}

	req.AddCookie(&http.Cookie{
		Name:  "Refresh-Token",
		Value: refreshToken,
	})

	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", errors.New(fmt.Sprintf("Unexpected status code. Expected 200, got %d", resp.StatusCode))
	}

	cookie := findCookieByName(resp.Cookies(), "Authorization")
	if cookie != nil {
		return cookie.Value, nil
	}

	return "", errors.New("Unexpected error")
}

func AuthMiddleware(roles ...string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			refreshToken, err := r.Cookie("Refresh-Token")
			if err != nil {
				http.Error(w, "Unauthorized", http.StatusUnauthorized)
				return
			}

			_, err = jwt.ParseWithClaims(refreshToken.Value, &jwt.RegisteredClaims{}, func(token *jwt.Token) (interface{}, error) {
				return SECRET, nil
			})
			if err != nil {
				http.Error(w, "Unauthorized", http.StatusUnauthorized)
				return
			}

			authCookie, err := r.Cookie("Authorization")
			var tokenString string

			if err == http.ErrNoCookie {
				tokenString, err = getAccessTokenByRefreshToken(refreshToken.Value)
				if err != nil {
					http.Error(w, "Unauthorized", http.StatusUnauthorized)
					return
				}

				http.SetCookie(w, &http.Cookie{
					Name:     "Authorization",
					Value:    tokenString,
					Path:     "/",
					HttpOnly: true,
					MaxAge:   31536000,
				})
			} else {
				tokenString = authCookie.Value
			}

			tokenString = strings.TrimPrefix(tokenString, "Bearer ")

			token, err := jwt.ParseWithClaims(tokenString, &claimsWithRoles{}, func(token *jwt.Token) (interface{}, error) {
				return SECRET, nil
			})
			if err != nil {
				http.Error(w, "Unauthorized", http.StatusUnauthorized)
				return
			}

			claims := token.Claims.(*claimsWithRoles)

			var claimsRoles []string
			err = json.Unmarshal(claims.Roles, &claimsRoles)
			if err != nil {
				http.Error(w, "Internal Server Error", http.StatusInternalServerError)
				return
			}

			for _, role := range roles {
				for _, claimRole := range claimsRoles {
					if role == claimRole {
						next.ServeHTTP(w, r)
						return
					}
				}
			}

			http.Error(w, "You do not have the necessary permissions", http.StatusUnauthorized)
		})
	}
}

func GetUserIDByAccessToken(accessToken string) (uint, error) {
	accessToken = strings.TrimPrefix(accessToken, "Bearer ")

	token, err := jwt.ParseWithClaims(accessToken, &claimsWithRoles{}, func(token *jwt.Token) (interface{}, error) {
		return SECRET, nil
	})
	if err != nil {
		return 0, err
	}

	claims := token.Claims.(*claimsWithRoles)
	userID, err := strconv.ParseUint(claims.RegisteredClaims.Subject, 10, 64)
	return uint(userID), err
}
