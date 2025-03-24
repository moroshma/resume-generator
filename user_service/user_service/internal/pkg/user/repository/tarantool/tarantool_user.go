package tarantool

import (
	"encoding/json"
	"errors"
	"fmt"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/models"
	"github.com/tarantool/go-tarantool/v2"
	"log/slog"
)

type tarantoolUserRepository struct {
	conn *tarantool.Connection
}

func NewTarantoolUserRepository(db *tarantool.Connection) models.UserRepositoryI {
	return &tarantoolUserRepository{db}
}

func (p tarantoolUserRepository) CreateUser(user models.User) (uint, error) {
	request := tarantool.NewCallRequest("create_new_user").Args([]interface{}{user.Login, user.Password})
	resp, err := p.conn.Do(request).Get()
	if err != nil {
		return 0, err
	}

	if len(resp) == 0 {
		return 0, errors.New("error create new user")
	}

	data := resp[0].(map[interface{}]interface{})
	if len(data) == 0 {
		return 0, fmt.Errorf("invalid response format")
	}

	var retUser models.User
	for k, v := range data {
		key, ok := k.(string)
		if !ok {
			return 0, fmt.Errorf("invalid response format")
		}
		switch key {
		case "status":
			status, ok := v.(uint8)
			if !ok {
				return 0, fmt.Errorf("invalid response format")
			}
			if status != 200 {
				return 0, fmt.Errorf("error create new user, %v", resp)
			}
		case "body":
			checkErr := CheckErrorResponse(v.(string))

			if checkErr.HasError() {
				return 0, checkErr
			}

			err = json.Unmarshal([]byte(v.(string)), &retUser)
			if err != nil {
				return 0, err
			}
		case "headers":
			continue
		default:
			slog.Any("invalid response format CreateUser", k)
		}
	}

	return retUser.ID, nil
}

func (p tarantoolUserRepository) CreateUserInfo(info models.UserInfo) error {
	// Сериализуем информацию о пользователе в JSON
	jsonData, err := json.Marshal(info)
	if err != nil {
		return fmt.Errorf("error marshaling user info: %w", err)
	}

	// Создаем запрос к Tarantool
	request := tarantool.NewCallRequest("create_user_info").Args([]interface{}{string(jsonData)})
	_, err = p.conn.Do(request).Get()
	if err != nil {
		return fmt.Errorf("error calling create_user_info: %w", err)
	}

	return nil
}

func (p tarantoolUserRepository) UpdateUserInfo(u uint, info models.UserInfo) error {
	//TODO implement me
	panic("implement me")
}

func (p tarantoolUserRepository) GetUserInfo(id uint) (models.UserInfo, error) {
	// Создаем запрос к Tarantool
	request := tarantool.NewCallRequest("get_user_info").Args([]interface{}{id})
	resp, err := p.conn.Do(request).Get()
	if err != nil {
		return models.UserInfo{}, fmt.Errorf("error calling get_user_info: %w", err)
	}

	if len(resp) == 0 {
		return models.UserInfo{}, errors.New("empty response from get_user_info")
	}

	data := resp[0].(map[interface{}]interface{})
	if len(data) == 0 {
		return models.UserInfo{}, fmt.Errorf("invalid response format")
	}

	var userInfo models.UserInfo
	for k, v := range data {
		key, ok := k.(string)
		if !ok {
			return models.UserInfo{}, fmt.Errorf("invalid response format")
		}
		switch key {
		case "status":
			status, ok := v.(uint8)
			if !ok {
				return models.UserInfo{}, fmt.Errorf("invalid response format")
			}
			if status != 200 {
				return models.UserInfo{}, fmt.Errorf("error getting user info, %v", resp)
			}
		case "body":
			checkErr := CheckErrorResponse(v.(string))
			if checkErr.HasError() {
				return models.UserInfo{}, checkErr
			}

			err = json.Unmarshal([]byte(v.(string)), &userInfo)
			if err != nil {
				return models.UserInfo{}, fmt.Errorf("error unmarshaling response: %w", err)
			}
		}
	}

	return userInfo, nil
}

func (p tarantoolUserRepository) Authenticate(user models.User) (models.User, error) {
	panic("implement me")
}

func (p tarantoolUserRepository) GetUserByLogin(login string) (models.User, error) {
	request := tarantool.NewCallRequest("get_user_by_login").Args([]interface{}{login})
	resp, err := p.conn.Do(request).Get()
	if err != nil {
		return models.User{}, err
	}

	if len(resp) == 0 {
		return models.User{}, errors.New("error login user")
	}

	data := resp[0].(map[interface{}]interface{})
	if len(data) == 0 {
		return models.User{}, fmt.Errorf("invalid response format")
	}

	var retUser models.User
	for k, v := range data {
		key, ok := k.(string)
		if !ok {
			return models.User{}, fmt.Errorf("invalid response format")
		}
		switch key {
		case "status":
			status, ok := v.(uint8)
			if !ok {
				return models.User{}, fmt.Errorf("invalid response format")
			}
			if status != 200 {
				return models.User{}, fmt.Errorf("error login, %v", resp)
			}
		case "body":
			checkErr := CheckErrorResponse(v.(string))

			if checkErr.HasError() {
				return models.User{}, checkErr
			}

			err = json.Unmarshal([]byte(v.(string)), &retUser)
			if err != nil {
				return models.User{}, err
			}
		case "headers":
			continue
		default:
			slog.Any("invalid response format GetUserByLogin", k)
		}
	}

	return retUser, nil
}
