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

func (p tarantoolUserRepository) CreateUserInfo(info models.UserInfo) (uint, error) {
	// Сериализуем информацию о пользователе в JSON
	jsonData, err := json.Marshal(info)
	if err != nil {
		return 0, fmt.Errorf("error marshaling user info: %w", err)
	}

	// Создаем запрос к Tarantool
	request := tarantool.NewCallRequest("create_user_info").Args([]interface{}{string(jsonData)})
	resp, err := p.conn.Do(request).Get()
	if err != nil {
		return 0, fmt.Errorf("error calling create_user_info: %w", err)
	}

	if len(resp) == 0 {
		return 0, errors.New("empty response from create_user_info")
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
				return 0, fmt.Errorf("error unmarshaling response: %w", err)
			}
		case "headers":
			continue
		default:
			slog.Any("invalid response format CreateUserInfo", k)
		}
	}

	return retUser.ID, nil
}

func (p tarantoolUserRepository) UpdateUserInfo(u uint, info models.UserInfo) error {
	//TODO implement me
	panic("implement me")
}

func (p tarantoolUserRepository) GetUserInfo(id uint) (models.UserInfo, error) {
	mockUserInfo := models.UserInfo{
		Name:        "John",
		Surname:     "Doe",
		Email:       "john.doe@example.com",
		Github:      "johndoe",
		PhoneNumber: "+123456789",
		Location:    "City, Country",
		Education: []models.Education{
			{
				Institution: "University X",
				Degree:      "Bachelor of Science",
				From:        "2010",
				To:          "2014",
			},
		},
		Experience: []models.Experience{
			{
				Company:     "Company Y",
				Role:        "Software Engineer",
				From:        "2015-01",
				To:          "2018-12",
				Description: "Worked on several high-impact projects.",
			},
		},
		SocialProfiles: models.SocialProfiles{
			Linkedin: "https://linkedin.com/in/johndoe",
			Telegram: "johndoe_telegram",
		},
		Languages: []string{"English", "Russian"},
	}

	return mockUserInfo, nil
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
