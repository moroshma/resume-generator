package models

type User struct {
	ID       uint   `json:"id,omitempty"`
	Login    string `json:"login,required"`
	Password string `json:"password,required"`
}

type UserInfo struct {
	UserID         uint           `json:"user_id,omitempty"`
	Name           string         `json:"name,omitempty"`
	Surname        string         `json:"surname,omitempty"`
	Email          string         `json:"email,omitempty"`
	Github         string         `json:"github,omitempty"`
	PhoneNumber    string         `json:"phone_number,omitempty"`
	Location       string         `json:"location,omitempty"`
	Education      []Education    `json:"education,omitempty"`
	Experience     []Experience   `json:"experience,omitempty"`
	SocialProfiles SocialProfiles `json:"social_profiles,omitempty"`
	Languages      []Language     `json:"languages,omitempty"`
}

type Language struct {
	LanguageID   uint   `json:"language_id,omitempty"`
	LanguageName string `json:"language,omitempty"`
}

type Education struct {
	EducationID *uint  `json:"education_id,omitempty"`
	Institution string `json:"institution,omitempty"`
	Degree      string `json:"degree,omitempty"`
	From        string `json:"from,omitempty"`
	To          string `json:"to,omitempty"`
}

type Experience struct {
	ExperienceID *uint  `json:"experience_id,omitempty"`
	Company      string `json:"company,omitempty"`
	Role         string `json:"role,omitempty"`
	From         string `json:"from,omitempty"`
	To           string `json:"to,omitempty"`
	Description  string `json:"description,omitempty"`
}

type SocialProfiles struct {
	Linkedin string `json:"linkedin,omitempty"`
	Telegram string `json:"telegram,omitempty"`
}

type UserUseCaseI interface {
	CreateUser(User) (uint, error)
	CreateUserInfo(UserInfo) error
	UpdateUserInfo(uint, UserInfo) (UserInfo, error)
	GetUserInfo(id uint) (UserInfo, error)
	Authenticate(User) (User, error)
}

type UserRepositoryI interface {
	CreateUser(User) (uint, error)
	CreateUserInfo(UserInfo) error
	UpdateUserInfo(UserInfo) (UserInfo, error)
	GetUserInfo(id uint) (UserInfo, error)
	GetUserByLogin(login string) (User, error)
}
