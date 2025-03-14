package app

import (
	"context"
	"fmt"
	"log"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/moroshma/resume-generator/user_service/internal/app/config"
	"github.com/moroshma/resume-generator/user_service/internal/app/middleware"
	auth_handlers "github.com/moroshma/resume-generator/user_service/internal/pkg/auth/delivery/http"
	token_usecase "github.com/moroshma/resume-generator/user_service/internal/pkg/auth/token/usecase"
	role_handlers "github.com/moroshma/resume-generator/user_service/internal/pkg/role/delivery/http"
	role_repository "github.com/moroshma/resume-generator/user_service/internal/pkg/role/repository/postgresql"
	role_usecase "github.com/moroshma/resume-generator/user_service/internal/pkg/role/usecase"
	user_handlers "github.com/moroshma/resume-generator/user_service/internal/pkg/user/delivery/http"
	user_repository "github.com/moroshma/resume-generator/user_service/internal/pkg/user/repository/postgresql"
	user_usecase "github.com/moroshma/resume-generator/user_service/internal/pkg/user/usecase"

	_ "github.com/moroshma/resume-generator/user_service/docs"
	httpSwagger "github.com/swaggo/http-swagger/v2"
)

func Run() {
	configPath := "/config/config.yaml"
	cfg, err := config.LoadConfig(configPath)
	if err != nil {
		log.Fatalf("Error loading config: %v", err)
	}

	r := chi.NewRouter()
	r.Use(middleware.CORSMiddleware())

	dbUser := cfg.UserService.Database.User
	dbPassword := cfg.UserService.Database.Password
	dbName := cfg.UserService.Database.Name
	httpHost := cfg.UserService.HTTP.Host
	httpPort := cfg.UserService.HTTP.Port

	dbURL := fmt.Sprintf("postgres://%s:%s@users_db:5432/%s", dbUser, dbPassword, dbName)
	dbpool, err := pgxpool.New(context.Background(), dbURL)
	if err != nil {
		log.Fatalf("Unable to create connection pool: %v\n", err)
	}
	defer dbpool.Close()

	err = dbpool.Ping(context.Background())
	if err != nil {
		log.Fatalf("Unable to ping connection pool: %v\n", err)
	}

	tokenUsecase := token_usecase.NewTokenUsecase()
	userUsecase := user_usecase.NewUserUsecase(user_repository.NewPsqlUserRepository(dbpool))
	roleUsecase := role_usecase.NewRoleUsecase(role_repository.NewPsqlRoleRepository(dbpool))

	auth_handlers.NewAuthHandlers(r, userUsecase, tokenUsecase, roleUsecase)
	role_handlers.NewRoleHandlers(r, roleUsecase)
	user_handlers.NewUserHandlers(r, userUsecase)

	r.Get("/swagger/*", httpSwagger.Handler(
		httpSwagger.URL("/user_service/swagger/doc.json"),
	))

	httpAddress := fmt.Sprintf("%s:%s", httpHost, httpPort)
	log.Printf("Starting server at %s", httpAddress)
	http.ListenAndServe(httpAddress, r)
}
