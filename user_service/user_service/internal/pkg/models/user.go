package models

type User struct {
	ID       uint   `json:"id,omitempty"`
	Login    string `json:"login,omitempty"`
	Password string `json:"password,omitempty"`
	Roles    []Role `json:"roles,omitempty"`
}

type UserUsecaseI interface {
	UsecaseI[User]
	Authenticate(User) (User, error)
}

type UserRepositoryI interface {
	RepositoryI[User]
	GetUserByLogin(string) (User, error)
}
