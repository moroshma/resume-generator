package middleware

import (
	"errors"
	"net/http"
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

			req, err := http.NewRequest("GET", authHost+"/api/v001/auth/check", nil)
			if err != nil {
				http.Error(w, "Server Error err:"+err.Error(), http.StatusInternalServerError)
				return
			}

			authCookie, err := r.Cookie("Authorization")
			if !errors.Is(err, http.ErrNoCookie) {
				req.AddCookie(authCookie)
			}
			req.AddCookie(refreshToken)

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

			next.ServeHTTP(w, r)
		})
	}
}
