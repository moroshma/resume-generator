package tarantool

import (
	"encoding/json"
	"errors"
	"fmt"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/models"
	"github.com/tarantool/go-tarantool/v2"
	"strings"
)

type tarantoolUserRepository struct {
	conn *tarantool.Connection
}

func NewTarantoolUserRepository(db *tarantool.Connection) models.UserRepositoryI {
	return &tarantoolUserRepository{db}
}

var CollisionCrateUser = errors.New("user with this login already exists")
var UserInfoNotFound = errors.New("user info not found")

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

	retUser, err := processTarantoolResponse[models.User](data)

	if err != nil {
		if strings.Contains(err.Error(), "user with this login already exists") {
			return 0, CollisionCrateUser
		}
		return 0, err
	}

	return retUser.ID, nil
}

func (p tarantoolUserRepository) CreateUserInfo(info models.UserInfo) error {
	jsonData, err := json.Marshal(info)
	if err != nil {
		return fmt.Errorf("error marshaling user info: %w", err)
	}

	request := tarantool.NewCallRequest("create_user_info").Args([]interface{}{string(jsonData)})
	resp, err := p.conn.Do(request).Get()
	if err != nil {
		return fmt.Errorf("error calling get_user_info: %w", err)
	}

	if len(resp) == 0 {
		return errors.New("empty response from get_user_info")
	}

	data := resp[0].(map[interface{}]interface{})
	if len(data) == 0 {
		return fmt.Errorf("invalid response format")
	}

	return checkErrorResponse(data)
}

func (p tarantoolUserRepository) UpdateUserInfo(info models.UserInfo) (models.UserInfo, error) {
	jsonData, err := json.Marshal(info)
	if err != nil {
		return models.UserInfo{}, fmt.Errorf("error marshalling user info: %w", err)
	}

	request := tarantool.NewCallRequest("update_user_info").Args([]interface{}{string(jsonData)})
	resp, err := p.conn.Do(request).Get()
	if err != nil {
		return models.UserInfo{}, fmt.Errorf("error calling update_user_info: %w", err)
	}

	if len(resp) == 0 {
		return models.UserInfo{}, fmt.Errorf("empty response from update_user_info")
	}

	data, ok := resp[0].(map[interface{}]interface{})
	if !ok || len(data) == 0 {
		return models.UserInfo{}, fmt.Errorf("invalid response from update_user_info")
	}

	_, err = processTarantoolResponse[models.UserInfo](data)

	return p.GetUserInfo(info.UserID)
}

func (p tarantoolUserRepository) GetUserInfo(id uint) (models.UserInfo, error) {
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
	userInfo, err := processTarantoolResponse[models.UserInfo](data)

	if err != nil {
		return models.UserInfo{}, fmt.Errorf("error processing response: %w", err)
	}

	return userInfo, nil
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

	retUser, err := processTarantoolResponse[models.User](data)

	if err != nil {
		return models.User{}, fmt.Errorf("error processing response: %v", err)
	}

	return retUser, nil
}

func (p tarantoolUserRepository) DeleteUserInfo(info models.DeleteUserInfo) error {
	jsonData, err := json.Marshal(info)
	if err != nil {
		return fmt.Errorf("error marshalling user info: %w", err)
	}

	request := tarantool.NewCallRequest("delete_user_info").Args([]interface{}{string(jsonData)})
	resp, err := p.conn.Do(request).Get()
	if err != nil {
		return fmt.Errorf("error calling delete_user_info: %w", err)
	}

	if len(resp) == 0 {
		return errors.New("empty response from delete_user_info")
	}

	data := resp[0].(map[interface{}]interface{})
	if len(data) == 0 {
		return fmt.Errorf("invalid response format")
	}

	return checkErrorResponse(data)
}
