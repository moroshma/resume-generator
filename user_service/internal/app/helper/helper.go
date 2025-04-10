package helper

import (
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
)

type APIError struct {
	Code    int `json:"code"`
	Message any `json:"message"`
}

func (e APIError) Error() string {
	return fmt.Sprintf("api error%d: %s", e.Code, e.Message)
}

func NewAPIError(code int, message string) APIError {
	return APIError{
		Code:    code,
		Message: message,
	}
}

func InvalidRequestData(errors map[string]string) APIError {
	return APIError{
		Code:    http.StatusUnprocessableEntity,
		Message: errors,
	}
}
func InvalidJson() APIError {
	return APIError{
		Code:    http.StatusBadRequest,
		Message: "Invalid JSON request data",
	}
}

type APIFunc func(w http.ResponseWriter, r *http.Request) error

func Make(h APIFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if err := h(w, r); err != nil {
			if apiErr, ok := err.(APIError); ok {
				writeJSON(w, apiErr.Code, apiErr)
			} else {
				errResp := map[string]any{
					"status":  http.StatusInternalServerError,
					"message": "Internal Server Error",
				}
				writeJSON(w, apiErr.Code, errResp)
			}
			slog.Error("HTTP error", slog.String("error", err.Error()), "path", r.URL.Path)
		}
	}
}

func writeJSON(w http.ResponseWriter, status int, data any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(data); err != nil {
		slog.Error("Failed to write JSON response", slog.String("error", err.Error()))
	}
}
