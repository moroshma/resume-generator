package models

type User struct {
	ID       uint   `json:"id,omitempty"`
	Login    string `json:"login,omitempty"`
	Password string `json:"password,omitempty"`
}

type UserInfo struct {
	Name           string         `json:"name,required"`
	Surname        string         `json:"surname,required"`
	Email          string         `json:"email,omitempty"`
	Github         string         `json:"github,omitempty"`
	PhoneNumber    string         `json:"phone_number,omitempty"`
	Location       string         `json:"location,omitempty"`
	Education      []Education    `json:"education,omitempty"`
	Experience     []Experience   `json:"experience,omitempty"`
	SocialProfiles SocialProfiles `json:"social_profiles,omitempty"`
	Languages      []string       `json:"languages,omitempty"`
}

type Education struct {
	Institution string `json:"institution,required"`
	Degree      string `json:"degree,required"`
	From        string `json:"from,required"`
	To          string `json:"to,omitempty"`
}

type Experience struct {
	Company     string `json:"company,required"`
	Role        string `json:"role,required"`
	From        string `json:"from,required"`
	To          string `json:"to,omitempty"`
	Description string `json:"description,omitempty"`
}

type SocialProfiles struct {
	Linkedin string `json:"linkedin,omitempty"`
	Telegram string `json:"telegram,omitempty"`
}

type UserUseCaseI interface {
	CreateUser(User) (uint, error)
	CreateUserInfo(UserInfo) (uint, error)
	UpdateUserInfo(uint, UserInfo) error
	GetUserInfo(id uint) (UserInfo, error)
	Authenticate(User) (User, error)
}

type UserRepositoryI interface {
	CreateUser(User) (uint, error)
	CreateUserInfo(UserInfo) (uint, error)
	UpdateUserInfo(uint, UserInfo) error
	GetUserInfo(id uint) (UserInfo, error)
	GetUserByLogin(login string) (User, error)
	Authenticate(User) (User, error)
}
