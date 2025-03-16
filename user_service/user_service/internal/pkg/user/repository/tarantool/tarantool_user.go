package tarantool

import (
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/models"
)

type tarantoolUserRepository struct {
	db *pgxpool.Pool
}

func (p tarantoolUserRepository) CreateUser(user models.User) (uint, error) {
	//TODO implement me
	panic("implement me")
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

func NewPsqlUserRepository(db *pgxpool.Pool) models.UserRepositoryI {
	return &tarantoolUserRepository{db}
}
