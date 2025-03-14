package models

import (
	"encoding/json"
)

type Role struct {
	ID   uint   `json:"id"`
	Name string `json:"name"`
}

type RoleUsecaseI interface {
	UsecaseI[Role]
	GetRolesByUserID(uint) (json.RawMessage, error)
}

type RoleRepositoryI interface {
	RepositoryI[Role]
	GetRolesByUserID(uint) (json.RawMessage, error)
}
