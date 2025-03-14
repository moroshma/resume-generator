package usecase

import (
	"encoding/json"
	"net/mail"

	"github.com/moroshma/resume-generator/user_service/internal/pkg/models"
	"golang.org/x/crypto/bcrypt"
)

type userUsercase struct {
	userRepository models.UserRepositoryI
}

func NewUserUsecase(userRepository models.UserRepositoryI) models.UserUsecaseI {
	return &userUsercase{userRepository}
}

func validateUser(user models.User) error {
	_, err := mail.ParseAddress(user.Login)
	return err
}

func (uc *userUsercase) Create(user models.User) (uint, error) {
	err := validateUser(user)
	if err != nil {
		return 0, err
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(user.Password), bcrypt.DefaultCost)
	if err != nil {
		return 0, err
	}
	user.Password = string(hashedPassword)

	return uc.userRepository.Create(user)
}

func (uc *userUsercase) Get(id uint) (json.RawMessage, error) {
	return uc.userRepository.Get(id)
}

func (uc *userUsercase) GetAll() (json.RawMessage, error) {
	return uc.userRepository.GetAll()
}

func (uc *userUsercase) Update(id uint, user models.User) error {
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(user.Password), bcrypt.DefaultCost)
	if err != nil {
		return err
	}
	user.Password = string(hashedPassword)

	err = validateUser(user)
	if err != nil {
		return err
	}

	user.ID = id
	return uc.userRepository.Update(user)
}

func (uc *userUsercase) Delete(id uint) error {
	return uc.userRepository.Delete(id)
}

func (uc *userUsercase) Authenticate(user models.User) (models.User, error) {
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
