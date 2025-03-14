package models

import "encoding/json"

type UsecaseI[T any] interface {
	Create(T) (uint, error)
	Get(uint) (json.RawMessage, error)
	GetAll() (json.RawMessage, error)
	Update(uint, T) error
	Delete(uint) error
}

type RepositoryI[T any] interface {
	Create(T) (uint, error)
	Get(uint) (json.RawMessage, error)
	GetAll() (json.RawMessage, error)
	Update(T) error
	Delete(uint) error
}
