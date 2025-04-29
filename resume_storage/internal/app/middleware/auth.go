package middleware

import (
	"log/slog"
	"net/http"

	auth_utils "github.com/moroshma/resume-generator/user_service/pkg/utils"
)

var client = http.Client{}

func AuthMiddleware(authHost string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			refreshToken, err := r.Cookie("Refresh-Token")
			if err != nil {
				http.Error(w, "[AuthMiddleware] Unauthorized Cant find Refresh-Token", http.StatusUnauthorized)
				return
			}

			authCookie, err := r.Cookie("Authorization")
			if err != nil {
				http.Error(w, "[AuthMiddleware] Unauthorized Cant find Authorization", http.StatusUnauthorized)
				return
			}

			req, err := http.NewRequest("GET", authHost+"/api/v001/auth/check", nil)
			if err != nil {
				http.Error(w, "Server Error err:"+err.Error(), http.StatusInternalServerError)
				return
			}

			req.AddCookie(&http.Cookie{
				Name:  "Refresh-Token",
				Value: refreshToken.Value,
			})
			req.AddCookie(&http.Cookie{
				Name:  "Authorization",
				Value: authCookie.Value,
			})

			resp, err := client.Do(req)
			if err != nil {
				http.Error(w, "Authentication Service Unavailable"+err.Error(), http.StatusServiceUnavailable)
				return
			}
			defer resp.Body.Close()

			if resp.StatusCode != http.StatusNoContent {
				http.Error(w, "Unauthorized", http.StatusUnauthorized)
				return
			}

			var respRefreshCookie string
			var respAccessCookie string
			for _, cookie := range resp.Cookies() {
				if cookie.Name == "Refresh-Token" {
					respRefreshCookie = cookie.Value
				}
				if cookie.Name == "Authorization" {
					respAccessCookie = cookie.Value
				}
			}

			if refreshToken.Value != "" && respAccessCookie != "" {
				slog.Any("set new respRefreshCookie", respRefreshCookie)
				slog.Any("set new respAccessCookie", respAccessCookie)

				auth_utils.SetAccessTokenRequestCookie(req, respAccessCookie)
				auth_utils.SetRefreshTokenCookie(w, respRefreshCookie)
				auth_utils.SetAccessTokenCookie(w, respAccessCookie)
			}

			next.ServeHTTP(w, r)
		})
	}
}
