package middleware

import (
	"net/http"
)

var client = http.Client{}

func AuthMiddleware() func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			refreshToken, err := r.Cookie("Refresh-Token")
			if err != nil {
				http.Error(w, "Unauthorized", http.StatusUnauthorized)
				return
			}

			authCookie, err := r.Cookie("Authorization")
			if err != nil {
				http.Error(w, "Unauthorized", http.StatusUnauthorized)
				return
			}

			req, err := http.NewRequest("GET", "http://localhost:8099/api/v001/auth/check", nil)
			if err != nil {
				http.Error(w, "Server Error", http.StatusInternalServerError)
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
				http.Error(w, "Authentication Service Unavailable", http.StatusServiceUnavailable)
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

			if refreshToken.Value != respRefreshCookie && respAccessCookie != "" {
				http.SetCookie(w, &http.Cookie{
					Name:     "Refresh-Token",
					Value:    respRefreshCookie,
					Path:     "/",
					HttpOnly: true,
				})
				http.SetCookie(w, &http.Cookie{
					Name:     "Authorization",
					Value:    respAccessCookie,
					Path:     "/",
					HttpOnly: true,
				})
			}

			next.ServeHTTP(w, r)
		})
	}
}
