package app

import (
	"fmt"
	"log"
	"net/http"

	"github.com/go-chi/chi/v5"
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
	configPath := "./config/config.yaml"
	cfg, err := config.LoadConfig(configPath)
	if err != nil {
		log.Fatalf("Error loading config: %v", err)
	}

	r := chi.NewRouter()
	r.Use(middleware.CORSMiddleware())

	//dbUser := cfg.Database.User
	//dbPassword := cfg.Database.Password
	//dbName := cfg.Database.Name
	httpHost := cfg.HTTP.Host
	httpPort := cfg.HTTP.Port

	//dbURL := fmt.Sprintf("postgres://%s:%s@users_db:5432/%s", dbUser, dbPassword, dbName)
	//dbpool, err := pgxpool.New(context.Background(), dbURL)
	//if err != nil {
	//	log.Fatalf("Unable to create connection pool: %v\n", err)
	//}
	//defer dbpool.Close()
	//
	//err = dbpool.Ping(context.Background())
	//if err != nil {
	//	log.Fatalf("Unable to ping connection pool: %v\n", err)
	//}

	tokenUseCase := token_usecase.NewTokenUsecase()
	userUseCase := user_usecase.NewUserUseCase(user_repository.NewPsqlUserRepository(nil))

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
