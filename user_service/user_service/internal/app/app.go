package app

import (
	"context"
	"fmt"
	"github.com/tarantool/go-tarantool/v2"
	"log"
	"net/http"
	"time"

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
	// Configure connection options
	opts := tarantool.Opts{
		Timeout:       5 * time.Second,
		Reconnect:     1 * time.Second,
		MaxReconnects: 0,
		Notify:        make(chan tarantool.ConnEvent, 10),
	}

	// Establish the connection
	conn, err := tarantool.Connect(context.Background(), dialer, opts)
	if err != nil {
		log.Fatalf("Failed to connect: %s", err)
	}

	defer conn.Close()

	// Выполняем пинг
	if err := pingTarantool(conn); err != nil {
		log.Fatalf("Ping failed: %s", err)
	}

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
func pingTarantool(conn *tarantool.Connection) error {
	// Создаем ping запрос
	req := tarantool.NewPingRequest()

	// Выполняем запрос
	resp := conn.Do(req)

	// Ждем ответ
	_, err := resp.GetResponse()
	if err != nil {
		return fmt.Errorf("ping failed: %w", err)
	}

	return nil
}
