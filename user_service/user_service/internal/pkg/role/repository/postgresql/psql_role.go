package postgresql

import (
	"context"
	"encoding/json"
	"errors"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/moroshma/resume-generator/user_service/user_service/internal/pkg/models"
)

type psqlRoleRepository struct {
	db *pgxpool.Pool
}

func NewPsqlRoleRepository(db *pgxpool.Pool) models.RoleRepositoryI {
	return &psqlRoleRepository{db}
}

func (pgRepo *psqlRoleRepository) Create(role models.Role) (uint, error) {
	var insertedID uint
	err := pgRepo.db.QueryRow(context.Background(), "SELECT insert_role($1)", role.Name).Scan(&insertedID)
	return insertedID, err
}

func (pgRepo *psqlRoleRepository) Get(id uint) (json.RawMessage, error) {
	var roleJSON json.RawMessage
	err := pgRepo.db.QueryRow(context.Background(), "SELECT get_role_by_id($1)", id).Scan(&roleJSON)
	return roleJSON, err
}

func (pgRepo *psqlRoleRepository) GetAll() (json.RawMessage, error) {
	var rolesJSON json.RawMessage
	err := pgRepo.db.QueryRow(context.Background(), "SELECT get_all_roles()").Scan(&rolesJSON)
	return rolesJSON, err
}

func (pgRepo *psqlRoleRepository) Update(role models.Role) error {
	var rowsAffected uint
	err := pgRepo.db.QueryRow(context.Background(), "SELECT update_role($1, $2)", role.ID, role.Name).Scan(&rowsAffected)
	if err != nil {
		return err
	}

	if rowsAffected != 1 {
		return errors.New("Can't update enexisting row")
	}

	return nil
}

func (pgRepo *psqlRoleRepository) Delete(id uint) error {
	var rowsAffected uint
	err := pgRepo.db.QueryRow(context.Background(), "SELECT delete_role($1)", id).Scan(&rowsAffected)
	if err != nil {
		return err
	}

	if rowsAffected != 1 {
		return errors.New("Can't delete enexisting row")
	}

	return nil
}

func (pgRepo *psqlRoleRepository) GetRolesByUserID(id uint) (json.RawMessage, error) {
	var rolesJSON json.RawMessage
	err := pgRepo.db.QueryRow(context.Background(), "SELECT get_roles_by_user_id($1)", id).Scan(&rolesJSON)
	return rolesJSON, err
}
