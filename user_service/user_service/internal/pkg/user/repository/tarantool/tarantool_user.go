package tarantool

import (
	"errors"
	"fmt"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/models"
	"github.com/tarantool/go-tarantool/v2"
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

	// Получаем первый элемент массива
	data := resp[0].([]interface{})
	if len(data) == 0 {
		return 0, fmt.Errorf("invalid response format")
	}

	if v, ok := data[0].(int64); ok {
		return uint(v), nil
	}

	return 0, fmt.Errorf("error create new user, %v", resp)
}

func (p tarantoolUserRepository) CreateUserInfo(info models.UserInfo) (uint, error) {
	//TODO implement me
	panic("implement me")
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
	//TODO implement me
	panic("implement me")
}

func (p tarantoolUserRepository) GetUserByLogin(login string) (models.User, error) {
	//TODO implement me
	panic("implement me")
}
