package http

import (
	"encoding/json"
	"net/http"
	"strconv"

	"github.com/go-chi/chi/v5"
	"github.com/moroshma/resume-generator/user_service/internal/app/middleware"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/models"
)

type userHandlers struct {
	userUseCase models.UserUsecaseI
}

func NewUserHandlers(r *chi.Mux, userUsecase models.UserUsecaseI) {
	handlers := &userHandlers{userUsecase}

	r.Route("/users", func(r chi.Router) {
		r.Use(middleware.AuthMiddleware("admin"))

		r.Get("/", handlers.getAll)
		r.Route("/{id}", func(r chi.Router) {
			r.Get("/", handlers.get)
			r.Put("/", handlers.update)
			r.Delete("/", handlers.delete)
		})
	})
}

// get retrieves a user by its ID.
// @Summary Get a user by ID
// @Description Retrieve a user by its ID
// @Tags users
// @Accept json
// @Produce json
// @Param id path string true "User ID"
// @Success 200 {object} models.User "User object"
// @Failure 400 {string} string "Bad Request"
// @Failure 401 {string} string "Unauthorized"
// @Failure 404 {string} string "Not Found"
// @Router /users/{id} [get]
func (handlers *userHandlers) get(w http.ResponseWriter, r *http.Request) {
	idParam := chi.URLParam(r, "id")
	id, err := strconv.ParseUint(idParam, 10, 64)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	user, err := handlers.userUseCase.Get(uint(id))
	if err != nil {
		http.Error(w, err.Error(), http.StatusNotFound)
		return
	}

	if len(user) == 0 {
		w.WriteHeader(http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write(user)
}

// getAll retrieves all users.
// @Summary Get all users
// @Description Retrieve all users
// @Tags users
// @Accept json
// @Produce json
// @Success 200 {array} models.User "List of users"
// @Failure 401 {string} string "Unauthorized"
// @Failure 404 {string} string "Not Found"
// @Router /users [get]
func (handlers *userHandlers) getAll(w http.ResponseWriter, r *http.Request) {
	users, err := handlers.userUseCase.GetAll()
	if err != nil {
		http.Error(w, err.Error(), http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write(users)
}

// update updates an existing user by its ID.
// @Summary Update a user by ID
// @Description Update an existing user identified by its ID with the provided JSON body
// @Tags users
// @Accept json
// @Produce json
// @Param id path string true "User ID"
// @Param user body models.User true "Updated user object"
// @Success 200 {string} string "OK"
// @Failure 400 {string} string "Bad Request"
// @Failure 401 {string} string "Unauthorized"
// @Failure 500 {string} string "Internal Server Error"
// @Router /users/{id} [put]
func (handlers *userHandlers) update(w http.ResponseWriter, r *http.Request) {
	idParam := chi.URLParam(r, "id")
	id, err := strconv.ParseUint(idParam, 10, 64)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	var user models.User
	err = json.NewDecoder(r.Body).Decode(&user)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	err = handlers.userUseCase.Update(uint(id), user)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

// delete deletes a user by its ID.
// @Summary Delete a user by ID
// @Description Delete an existing user identified by its ID
// @Tags users
// @Accept json
// @Produce json
// @Param id path string true "User ID"
// @Success 200 {string} string "OK"
// @Failure 400 {string} string "Bad Request"
// @Failure 401 {string} string "Unauthorized"
// @Failure 404 {string} string "Not Found"
// @Router /users/{id} [delete]
func (handlers *userHandlers) delete(w http.ResponseWriter, r *http.Request) {
	idParam := chi.URLParam(r, "id")
	id, err := strconv.ParseUint(idParam, 10, 64)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	err = handlers.userUseCase.Delete(uint(id))
	if err != nil {
		http.Error(w, err.Error(), http.StatusNotFound)
		return
	}

	w.WriteHeader(http.StatusOK)
}
