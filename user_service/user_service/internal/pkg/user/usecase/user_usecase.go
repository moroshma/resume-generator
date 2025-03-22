package usecase

import (
	"github.com/moroshma/resume-generator/user_service/internal/pkg/models"
	"golang.org/x/crypto/bcrypt"
)

type userUseCase struct {
	userRepository models.UserRepositoryI
}

func NewUserUseCase(userRepository models.UserRepositoryI) models.UserUseCaseI {
	return &userUseCase{userRepository}
}

func (uc *userUseCase) CreateUser(user models.User) (uint, error) {
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(user.Password), bcrypt.DefaultCost)
	if err != nil {
		return 0, err
	}
	user.Password = string(hashedPassword)

	return uc.userRepository.CreateUser(user)
}

func (uc *userUseCase) CreateUserInfo(info models.UserInfo) (uint, error) {
	return uc.userRepository.CreateUserInfo(info)
}

func (uc *userUseCase) UpdateUserInfo(u2 uint, info models.UserInfo) error {
	//TODO implement me
	panic("implement me")
}

func (uc *userUseCase) GetUserInfo(id uint) (models.UserInfo, error) {
	return uc.userRepository.GetUserInfo(id)
}

func (uc *userUseCase) Create(user models.User) (uint, error) {
	panic("implement me")
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
