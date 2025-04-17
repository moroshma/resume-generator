package utils

import (
	"fmt"
	"net/http"
)

const (
	RefreshTokenName = "Refresh-Token"
	AuthTokenName    = "Authorization"
	cookiePath       = "/"
	refreshMaxAge    = 7 * 24 * 60 * 60
	accessMaxAge     = 15 * 60
)

func SetRefreshTokenCookie(w http.ResponseWriter, token string) {
	http.SetCookie(w, &http.Cookie{
		Name:     RefreshTokenName,
		Value:    token,
		Path:     cookiePath,
		HttpOnly: true,
		MaxAge:   refreshMaxAge,
		Secure:   false,
		SameSite: http.SameSiteStrictMode,
	})
}

func SetAccessTokenCookie(w http.ResponseWriter, token string) {
	http.SetCookie(w, &http.Cookie{
		Name:     AuthTokenName,
		Value:    fmt.Sprintf("Bearer %s", token),
		Path:     cookiePath,
		HttpOnly: true,
		MaxAge:   accessMaxAge,
		Secure:   false,
		SameSite: http.SameSiteStrictMode,
	})
}

func ClearRefreshTokenCookie(w http.ResponseWriter) {
	http.SetCookie(w, &http.Cookie{
		Name:     RefreshTokenName,
		Value:    "",
		Path:     cookiePath,
		HttpOnly: true,
		MaxAge:   -1,
		Secure:   false,
		SameSite: http.SameSiteStrictMode,
	})
}

func ClearAccessTokenCookie(w http.ResponseWriter) {
	http.SetCookie(w, &http.Cookie{
		Name:     AuthTokenName,
		Value:    "",
		Path:     cookiePath,
		HttpOnly: true,
		MaxAge:   -1,
		Secure:   false,
		SameSite: http.SameSiteStrictMode,
	})
}
