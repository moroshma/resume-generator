package usecase

import (
	"encoding/json"
	"errors"

	"github.com/moroshma/resume-generator/user_service/user_service/internal/pkg/models"
)

type roleUsecase struct {
	roleRepository models.RoleRepositoryI
}

func NewRoleUsecase(roleRepository models.RoleRepositoryI) models.RoleUsecaseI {
	return &roleUsecase{roleRepository}
}

func validateRole(role models.Role) error {
	if role.Name == "" {
		return errors.New("Role name must be non-empty")
	}

	return nil
}

func (uc *roleUsecase) Create(role models.Role) (uint, error) {
	err := validateRole(role)
	if err != nil {
		return 0, err
	}
	return uc.roleRepository.Create(role)
}

func (uc *roleUsecase) Get(id uint) (json.RawMessage, error) {
	return uc.roleRepository.Get(id)
}

func (uc *roleUsecase) GetAll() (json.RawMessage, error) {
	return uc.roleRepository.GetAll()
}

func (uc *roleUsecase) Update(id uint, role models.Role) error {
	role.ID = id

	err := validateRole(role)
	if err != nil {
		return err
	}

	return uc.roleRepository.Update(role)
}

func (uc *roleUsecase) Delete(id uint) error {
	return uc.roleRepository.Delete(id)
}

func (uc *roleUsecase) GetRolesByUserID(id uint) (json.RawMessage, error) {
	return uc.roleRepository.GetRolesByUserID(id)
}
