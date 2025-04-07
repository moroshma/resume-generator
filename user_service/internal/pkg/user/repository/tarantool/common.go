package tarantool

import (
	"encoding/json"
	"errors"
	"fmt"
)

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

func processTarantoolResponse[T any](data map[interface{}]interface{}) (T, error) {
	var result T
	var status uint8

	for k, v := range data {
		key, ok := k.(string)
		if !ok {
			var zero T
			return zero, fmt.Errorf("invalid response format")
		}

		switch key {
		case "status":
			status, ok = v.(uint8)
			if !ok {
				var zero T
				return zero, fmt.Errorf("invalid status value")
			}
		case "body":
			if v == nil {
				continue
			}

			bodyStr, ok := v.(string)
			if !ok {
				var zero T
				return zero, fmt.Errorf("body is not a string")
			}

			if bodyStr == "" {
				continue
			}

			checkErr := CheckErrorResponse(bodyStr)
			if checkErr.HasError() {
				var zero T
				return zero, checkErr
			}

			err := json.Unmarshal([]byte(bodyStr), &result)
			if err != nil {
				var zero T
				return zero, fmt.Errorf("error unmarshaling response: %w", err)
			}
		}
	}

	if status != 200 {
		return result, errors.New(fmt.Sprintf("error in response, status:%v", status))
	}

	return result, nil
}
