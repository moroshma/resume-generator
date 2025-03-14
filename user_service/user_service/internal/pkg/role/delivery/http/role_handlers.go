package http

import (
	"encoding/json"
	"net/http"
	"strconv"

	"github.com/go-chi/chi/v5"
	"github.com/moroshma/resume-generator/user_service/internal/app/middleware"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/models"
)

type roleHandlers struct {
	roleUsecase models.RoleUsecaseI
}

func NewRoleHandlers(r *chi.Mux, roleUsecase models.RoleUsecaseI) {
	handlers := &roleHandlers{roleUsecase}

	r.Route("/roles", func(r chi.Router) {
		r.Use(middleware.AuthMiddleware("admin"))

		r.Get("/", handlers.getAll)
		r.Post("/", handlers.create)
		r.Route("/{id}", func(r chi.Router) {
			r.Get("/", handlers.get)
			r.Put("/", handlers.update)
			r.Delete("/", handlers.delete)
		})
	})
}

// create creates a new role.
// @Summary Create a new role
// @Security JWT
// @Description Create a new role with the provided JSON body
// @Tags roles
// @Accept json
// @Produce json
// @Param role body models.Role true "Role object to be created"
// @Success 201 {string} string "Created"
// @Failure 400 {string} string "Bad Request"
// @Failure 401 {string} string "Unauthorized"
// @Failure 500 {string} string "Internal Server Error"
// @Router /roles [post]
func (handlers *roleHandlers) create(w http.ResponseWriter, r *http.Request) {
	var role models.Role
	err := json.NewDecoder(r.Body).Decode(&role)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	insertedID, err := handlers.roleUsecase.Create(role)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	role.ID = insertedID

	w.WriteHeader(http.StatusCreated)
}

// get retrieves a role by its ID.
// @Summary Get a role by ID
// @Security JWT
// @Description Retrieve a role by its ID
// @Tags roles
// @Accept json
// @Produce json
// @Param id path string true "Role ID"
// @Success 200 {object} models.Role "Role object"
// @Failure 400 {string} string "Bad Request"
// @Failure 401 {string} string "Unauthorized"
// @Failure 404 {string} string "Not Found"
// @Router /roles/{id} [get]
func (handlers *roleHandlers) get(w http.ResponseWriter, r *http.Request) {
	idParam := chi.URLParam(r, "id")
	id, err := strconv.ParseUint(idParam, 10, 64)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	role, err := handlers.roleUsecase.Get(uint(id))
	if err != nil {
		http.Error(w, err.Error(), http.StatusNotFound)
		return
	}

	if len(role) == 0 {
		w.WriteHeader(http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write(role)
}

// getAll retrieves all roles.
// @Summary Get all roles
// @Security JWT
// @Description Retrieve all roles
// @Tags roles
// @Accept json
// @Produce json
// @Success 200 {array} models.Role "List of roles"
// @Failure 401 {string} string "Unauthorized"
// @Failure 500 {string} string "Internal Server Error"
// @Router /roles [get]
func (handlers *roleHandlers) getAll(w http.ResponseWriter, r *http.Request) {
	roles, err := handlers.roleUsecase.GetAll()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write(roles)
}

// update updates an existing role by its ID.
// @Summary Update a role by ID
// @Security JWT
// @Description Update an existing role identified by its ID with the provided JSON body
// @Tags roles
// @Accept json
// @Produce json
// @Param id path string true "Role ID"
// @Param role body models.Role true "Updated role object"
// @Success 200 {string} string "OK"
// @Failure 400 {string} string "Bad Request"
// @Failure 401 {string} string "Unauthorized"
// @Failure 404 {string} string "Not Found"
// @Router /roles/{id} [put]
func (handlers *roleHandlers) update(w http.ResponseWriter, r *http.Request) {
	idParam := chi.URLParam(r, "id")
	id, err := strconv.ParseUint(idParam, 10, 64)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	var role models.Role
	err = json.NewDecoder(r.Body).Decode(&role)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	err = handlers.roleUsecase.Update(uint(id), role)
	if err != nil {
		http.Error(w, err.Error(), http.StatusNotFound)
		return
	}

	w.WriteHeader(http.StatusOK)
}

// delete deletes a role by its ID.
// @Summary Delete a role by ID
// @Security JWT
// @Description Delete an existing role identified by its ID
// @Tags roles
// @Accept json
// @Produce json
// @Param id path string true "Role ID"
// @Success 200 {string} string "OK"
// @Failure 400 {string} string "Bad Request"
// @Failure 401 {string} string "Unauthorized"
// @Failure 404 {string} string "Not Found"
// @Router /roles/{id} [delete]
func (handlers *roleHandlers) delete(w http.ResponseWriter, r *http.Request) {
	idParam := chi.URLParam(r, "id")
	id, err := strconv.ParseUint(idParam, 10, 64)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	err = handlers.roleUsecase.Delete(uint(id))
	if err != nil {
		http.Error(w, err.Error(), http.StatusNotFound)
		return
	}

	w.WriteHeader(http.StatusOK)
}
