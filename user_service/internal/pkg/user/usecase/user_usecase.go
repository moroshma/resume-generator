package usecase

import (
	"errors"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/models"
	"golang.org/x/crypto/bcrypt"
	"regexp"
)

var (
	loginRegex    = regexp.MustCompile(`^[a-zA-Z][a-zA-Z0-9_]{3,}$`)
	passwordRegex = regexp.MustCompile(`^[a-zA-Z0-9!@#$%^&*]{7,}$`)
)

type userUseCase struct {
	userRepository models.UserRepositoryI
}

func NewUserUseCase(userRepository models.UserRepositoryI) models.UserUseCaseI {
	return &userUseCase{userRepository}
}

func (uc *userUseCase) CreateUser(user models.User) (uint, error) {
	if len(user.Password) <= 6 || len(user.Login) < 4 {
		return 0, errors.New("password or login is too short")
	}

	if !loginRegex.MatchString(user.Login) {
		return 0, errors.New("invalid login format")
	}
	if !passwordRegex.MatchString(user.Password) {
		return 0, errors.New("invalid password format")
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(user.Password), bcrypt.DefaultCost)
	if err != nil {
		return 0, err
	}
	user.Password = string(hashedPassword)

	return uc.userRepository.CreateUser(user)
}

func (uc *userUseCase) CreateUserInfo(info models.UserInfo) error {

	return uc.userRepository.CreateUserInfo(info)
}

func (uc *userUseCase) UpdateUserInfo(userID uint, info models.UserInfo) (models.UserInfo, error) {
	info.UserID = userID

	return uc.userRepository.UpdateUserInfo(info)
}

func (uc *userUseCase) GetUserInfo(id uint) (models.UserInfo, error) {
	return uc.userRepository.GetUserInfo(id)
}

func (uc *userUseCase) Authenticate(user models.User) (models.User, error) {
	authUser, err := uc.userRepository.GetUserByLogin(user.Login)
	if err != nil {
		return models.User{}, err
	}

	err = bcrypt.CompareHashAndPassword([]byte(authUser.Password), []byte(user.Password))
	if err != nil {
		return models.User{}, err
	}

	return authUser, nil
}
