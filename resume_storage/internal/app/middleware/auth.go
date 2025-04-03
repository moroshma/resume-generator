package middleware

//import (
//	"errors"
//	"fmt"
//	"github.com/moroshma/resume-generator/user_service/internal/pkg/auth/token/usecase"
//	"net/http"
//	"strconv"
//	"strings"
//
//	"github.com/golang-jwt/jwt/v5"
//)
//
//type claims struct {
//	jwt.RegisteredClaims
//}
//
//var SECRET = []byte("private-key")
//
//var client http.Client
//
//func findCookieByName(cookies []*http.Cookie, name string) *http.Cookie {
//	for _, cookie := range cookies {
//		if cookie.Name == name {
//			return cookie
//		}
//	}
//	return nil
//}
//
//func getAccessTokenByRefreshToken(refreshToken string) (string, error) {
//	req, err := http.NewRequest("GET", "http://gateway/refresh", nil)
//	if err != nil {
//		return "", err
//	}
//
//	req.AddCookie(&http.Cookie{
//		Name:  "Refresh-Token",
//		Value: refreshToken,
//	})
//
//	resp, err := client.Do(req)
//	if err != nil {
//		return "", err
//	}
//	defer resp.Body.Close()
//
//	if resp.StatusCode != http.StatusOK {
//		return "", errors.New(fmt.Sprintf("Unexpected status code. Expected 200, got %d", resp.StatusCode))
//	}
//
//	cookie := findCookieByName(resp.Cookies(), "Authorization")
//	if cookie != nil {
//		return cookie.Value, nil
//	}
//
//	return "", errors.New("unexpected error")
//}
//
//func AuthMiddleware() func(http.Handler) http.Handler {
//	return func(next http.Handler) http.Handler {
//		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
//			refreshToken, err := r.Cookie("Refresh-Token")
//			if err != nil {
//				http.Error(w, "Unauthorized", http.StatusUnauthorized)
//				return
//			}
//
//			_, err = jwt.ParseWithClaims(refreshToken.Value, &jwt.RegisteredClaims{}, func(token *jwt.Token) (interface{}, error) {
//				return SECRET, nil
//			})
//			if err != nil {
//				http.Error(w, "Unauthorized", http.StatusUnauthorized)
//				return
//			}
//
//			authCookie, err := r.Cookie("Authorization")
//			var tokenString string
//
//			if errors.Is(err, http.ErrNoCookie) {
//				tokenString, err = getAccessTokenByRefreshToken(refreshToken.Value)
//				if err != nil {
//					http.Error(w, "Unauthorized", http.StatusUnauthorized)
//					return
//				}
//
//				http.SetCookie(w, &http.Cookie{
//					Name:     "Authorization",
//					Value:    tokenString,
//					Path:     "/",
//					HttpOnly: true,
//					MaxAge:   31536000,
//				})
//				next.ServeHTTP(w, r)
//			}
//
//			tokenString = authCookie.Value
//			parsedToken, err := jwt.ParseWithClaims(tokenString, &claims{}, func(token *jwt.Token) (interface{}, error) {
//				return SECRET, nil
//			})
//			if err != nil || !parsedToken.Valid {
//				tokenString, err = getAccessTokenByRefreshToken(refreshToken.Value)
//				if err != nil {
//					http.Error(w, "Unauthorized", http.StatusUnauthorized)
//					return
//				}
//
//				http.SetCookie(w, &http.Cookie{
//					Name:     "Authorization",
//					Value:    tokenString,
//					Path:     "/",
//					HttpOnly: true,
//					MaxAge:   31536000,
//				})
//			}
//
//			userID, err := GetUserIDByAccessToken(tokenString)
//			if err != nil {
//				http.Error(w, "Unauthorized", http.StatusUnauthorized)
//				return
//			}
//
//			newRefreshToken, err := usecase.NewTokenUseCase().GenerateRefreshTokenByUserID(userID)
//			if err != nil {
//				http.Error(w, err.Error(), http.StatusUnauthorized)
//				return
//			}
//
//			http.SetCookie(w, &http.Cookie{
//				Name:     "Refresh-Token",
//				Value:    newRefreshToken,
//				Path:     "/",
//				HttpOnly: true,
//			})
//
//			next.ServeHTTP(w, r)
//		})
//	}
//}
//
//func GetUserIDByAccessToken(accessToken string) (uint, error) {
//	accessToken = strings.TrimPrefix(accessToken, "Bearer ")
//
//	token, err := jwt.ParseWithClaims(accessToken, &claims{}, func(token *jwt.Token) (interface{}, error) {
//		return SECRET, nil
//	})
//	if err != nil {
//		return 0, err
//	}
//
//	claims := token.Claims.(*claims)
//	userID, err := strconv.ParseUint(claims.RegisteredClaims.Subject, 10, 64)
//	return uint(userID), err
//}
