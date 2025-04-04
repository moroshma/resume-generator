package app

import (
	"context"
	"fmt"
	"github.com/go-chi/chi/v5"
	chi_middelware "github.com/go-chi/chi/v5/middleware"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/moroshma/resume-generator/resume_storage/internal/app/config"
	"github.com/moroshma/resume-generator/resume_storage/internal/app/middleware"
	"github.com/moroshma/resume-generator/resume_storage/internal/resume/db/postgres"
	"github.com/moroshma/resume-generator/resume_storage/internal/resume/delivery/http"
	"github.com/moroshma/resume-generator/resume_storage/internal/resume/resume_storage"
	"github.com/moroshma/resume-generator/resume_storage/internal/resume/usecase"

	"log"
	"net/http"
)

func Run() {
	configPath := "./config/config.yaml"
	cfg, err := config.LoadConfig(configPath)
	if err != nil {
		log.Fatalf("Error loading config: %v", err)
	}

	r := chi.NewRouter()
	r.Use(chi_middelware.Logger)
	// add recovery middleware to catch panics
	r.Use(middleware.RecoverMiddleware())
	r.Use(middleware.CORSMiddleware())

	dbName := cfg.Database.Name
	dbUser := cfg.Database.User
	dbPassword := cfg.Database.Password

	dbHost := cfg.Database.Host
	httpHost := cfg.HTTP.Host
	httpPort := cfg.HTTP.Port

	objectStorageUser := cfg.ObjectStorage.User
	objectStoragePassword := cfg.ObjectStorage.Password
	objectStorageHost := cfg.ObjectStorage.Host

	dbConnString := "postgres://" + dbUser + ":" + dbPassword + "@" + dbHost + "/" + dbName
	connPool, err := pgxpool.New(context.Background(), dbConnString)
	if err != nil {
		log.Fatal("Error while creating connection to the database!!")
	}
	defer connPool.Close()

	err = connPool.Ping(context.Background())
	if err != nil {
		log.Fatal("Error while pinging the database!!")
	}

	mp, err := resume_storage.NewMinioProvider(objectStorageHost, objectStorageUser, objectStoragePassword, false)
	if err != nil {
		log.Fatal("Error while creating minio provider!!")
	}
	if err := mp.Connect(); err != nil {
		log.Fatal("Error while connecting to minio!!")
	}

	postgresProvider, err := postgres.NewPostgresProvider(connPool)
	if err != nil {
		log.Fatal("Error while creating postgres provider!!")
	}
	resumeUseCase := usecase.NewResumeUseCase(postgresProvider, mp)

	resume_handlers.NewResumeRoutes(r, resumeUseCase)

	httpAddress := fmt.Sprintf("%s:%s", httpHost, httpPort)
	log.Printf("Starting server at %s", httpAddress)
	err = http.ListenAndServe(httpAddress, r)

	if err != nil {
		log.Fatalf("Error starting server: %v", err)
		return
	}
}
