package app

import (
	"context"
	"fmt"
	"github.com/tarantool/go-tarantool/v2"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/go-chi/chi/v5"
	chi_middelware "github.com/go-chi/chi/v5/middleware"
	"github.com/moroshma/resume-generator/user_service/internal/app/config"
	"github.com/moroshma/resume-generator/user_service/internal/app/middleware"
	auth_handlers "github.com/moroshma/resume-generator/user_service/internal/pkg/auth/delivery/http"
	token_usecase "github.com/moroshma/resume-generator/user_service/internal/pkg/auth/token/usecase"
	user_handlers "github.com/moroshma/resume-generator/user_service/internal/pkg/user/delivery/http"
	user_repository "github.com/moroshma/resume-generator/user_service/internal/pkg/user/repository/tarantool"
	user_usecase "github.com/moroshma/resume-generator/user_service/internal/pkg/user/usecase"

	_ "github.com/moroshma/resume-generator/user_service/docs"
	httpSwagger "github.com/swaggo/http-swagger/v2"
)

func Run() {
	var configPath string
	if os.Getenv("APP_ENV") == "" || os.Getenv("APP_ENV") == "dev" {
		configPath = "./config/config_dev.yaml"
	} else {
		configPath = "./config/config_prod.yaml"
	}

	cfg, err := config.LoadConfig(configPath)
	if err != nil {
		log.Fatalf("Error loading config: %v", err)
	}

	r := chi.NewRouter()
	r.Use(middleware.RecoverMiddleware())
	r.Use(middleware.CORSMiddleware())
	r.Use(chi_middelware.Logger)

	//dbName := cfg.Database.Name
	dbUser := cfg.Database.User
	dbPassword := cfg.Database.Password
	dbHost := cfg.Database.Host
	httpHost := cfg.HTTP.Host
	httpPort := cfg.HTTP.Port

	dialer := tarantool.NetDialer{
		Address:  dbHost,
		User:     dbUser,
		Password: dbPassword,
	}

	opts := tarantool.Opts{
		Timeout:       5 * time.Second,
		Reconnect:     1 * time.Second,
		MaxReconnects: 0,
		Notify:        make(chan tarantool.ConnEvent, 10),
	}

	var conn *tarantool.Connection
	for i := 0; i < 5; i++ {
		conn, err = tarantool.Connect(context.Background(), dialer, opts)
		if err == nil {
			break
		}
		log.Printf("Failed to connect: %s. Retrying in 1 second...", err)
		time.Sleep(1 * time.Second)
	}

	if err != nil {
		log.Fatalf("Failed to connect after 5 attempts: %s", err)
	}

	defer conn.Close()

	tokenUseCase := token_usecase.NewTokenUseCase()
	userUseCase := user_usecase.NewUserUseCase(user_repository.NewTarantoolUserRepository(conn))

	auth_handlers.NewAuthHandlers(r, userUseCase, tokenUseCase)
	user_handlers.NewUserHandlers(r, userUseCase)

	r.Get("/swagger/*", httpSwagger.Handler(
		httpSwagger.URL("/user_service/swagger/doc.json"),
	))

	httpAddress := fmt.Sprintf("%s:%s", httpHost, httpPort)
	log.Printf("Starting server at %s", httpAddress)
	err = http.ListenAndServe(httpAddress, r)

	if err != nil {
		log.Fatalf("Error starting server: %v", err)
		return
	}
}
