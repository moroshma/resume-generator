package tarantool

import "encoding/json"

type ErrorResponse struct {
	Er string `json:"error,omitempty"`
}

func (e *ErrorResponse) Error() string {
	return e.Er
}

func (e *ErrorResponse) HasError() bool {
	return e.Er != ""
}

func CheckErrorResponse(body string) *ErrorResponse {
	er := &ErrorResponse{}
	err := json.Unmarshal([]byte(body), er)
	if err != nil {
		return &ErrorResponse{Er: err.Error()}
	}

	return er
}
