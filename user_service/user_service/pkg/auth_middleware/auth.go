package auth_middleware

import (
	"errors"
	"fmt"
	"net/http"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
)

type claimsWithRoles struct {
	jwt.RegisteredClaims
	UserID string `json:"user_id"`
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

func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		refreshToken, err := c.Cookie("Refresh-Token")
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
			c.Abort()
			return
		}

		_, err = jwt.ParseWithClaims(refreshToken, &jwt.RegisteredClaims{}, func(token *jwt.Token) (interface{}, error) {
			return SECRET, nil
		})
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
			c.Abort()
			return
		}

		tokenString, err := c.Cookie("Authorization")
		if errors.Is(err, http.ErrNoCookie) {
			tokenString, err = getAccessTokenByRefreshToken(refreshToken)
			if err != nil {
				c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
				c.Abort()
				return
			}

			c.SetCookie("Authorization", tokenString, 31536000, "/", "/", false, true)
		}

		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
			c.Abort()
			return
		}

		tokenString = strings.TrimPrefix(tokenString, "Bearer ")

		_, err = jwt.ParseWithClaims(tokenString, &claimsWithRoles{}, func(token *jwt.Token) (interface{}, error) {
			return SECRET, nil
		})
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
			c.Abort()
			return
		}

		c.Next()
	}
}

func GetUserIDByAccessToken(accessToken string) (uint, error) {
	// Access token доставайте из куков "Authorization"
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
