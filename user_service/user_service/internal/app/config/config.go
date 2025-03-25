package config

import (
	"log"

	"github.com/ilyakaznacheev/cleanenv"
)

type UserService struct {
	Database struct {
		User     string `yaml:"user" env:"DB_USER"`
		Password string `yaml:"password" env:"DB_PASSWORD"`
		Name     string `yaml:"name" env:"DB_NAME"`
		Host     string `yaml:"host" env:"DB_HOST" default:"localhost"`
	} `yaml:"database"`

	HTTP struct {
		Host string `yaml:"host" env:"HTTP_HOST"`
		Port string `yaml:"port" env:"HTTP_PORT"`
	} `yaml:"http"`
}

func LoadConfig(filepath string) (*UserService, error) {
	var cfg UserService
	if err := cleanenv.ReadConfig(filepath, &cfg); err != nil {
		log.Fatalf("Error reading config file: %v", err)
		return nil, err
	}

	if err := cleanenv.ReadEnv(&cfg); err != nil {
		log.Fatalf("Error reading environment variables: %v", err)
		return nil, err
	}

	return &cfg, nil
}
